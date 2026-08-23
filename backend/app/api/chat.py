from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import json

from backend.app.persona.service import PersonaService
from backend.app.memory.service import MemoryService
from backend.app.llm.router import LLMRouter
from backend.app.observability.langfuse import log_trace
from backend.app.safety.filter import check as safety_check
from backend.app.tools.registry import registry as tool_registry

router = APIRouter()

# Singletons — auto switch real LLM when OPENROUTER_API_KEY set
import os

persona_service = PersonaService(persona_dir="persona")
memory_service = MemoryService(qdrant_url=os.getenv("QDRANT_URL", "memory://test"), letta_url=os.getenv("LETTA_URL", "memory://test"))
_real_key = os.getenv("OPENROUTER_API_KEY")
if _real_key and _real_key != "dummy":
    llm_router = LLMRouter(api_key=_real_key, base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"), model=os.getenv("LLM_MODEL", "nvidia/nemotron-3-nano-30b-a3b:free"))
else:
    llm_router = LLMRouter(api_key="dummy", base_url="memory://test")


class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: str | None = None


@router.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    user_id = req.user_id
    message = req.message

    # 0. safety
    safety = safety_check(message)
    if safety["risk"] == "high":
        log_trace("safety.block", {"user_id": user_id, "risk": "high"})
        crisis = safety["crisis"]

        def blocked():
            yield f"data: {json.dumps({'chunk': f'我注意到你可能需要帮助：{crisis}'}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'chunk': '如果你需要，请告诉我，我在这里陪你。'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(blocked(), media_type="text/event-stream")

    # 0.5 tool auto-call (simple heuristic)
    tool_result = None
    if any(kw in message for kw in ["日历", "日程", "会议"]):
        try:
            tool_result = tool_registry.call("calendar", {"user_id": user_id, "date": "2026-08-22"})
        except Exception:
            pass
    elif "搜索" in message:
        q = message.replace("搜索", "").strip() or message
        try:
            tool_result = tool_registry.call("search", {"query": q})
        except Exception:
            pass
    elif any(kw in message for kw in ["记一下", "备忘", "记住"]):
        try:
            tool_registry.call("memo", {"user_id": user_id, "content": message})
        except Exception:
            pass

    # 1. recall
    hits = memory_service.recall(user_id=user_id, query=message, limit=8)
    mem_texts = [h.content for h in hits]
    if tool_result:
        mem_texts.append(f"工具结果: {tool_result}")
    log_trace("memory.recall", {"user_id": user_id, "query": message, "hits": len(hits)})

    # 2. persona
    persona_prompt = persona_service.build_system_prompt(user_id=user_id)
    log_trace("chat.completions", {"user_id": user_id, "message": message, "memories": mem_texts})

    # 3. stream via LLM
    def generate():
        # SSE format
        for chunk in llm_router.stream(user_id=user_id, message=message, persona_prompt=persona_prompt, memories=mem_texts):
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        # persist memory after stream (very naive fact detection)
        # keep it simple for TDD: store if looks like a fact and not a question
        is_question = any(q in message for q in ["什么", "吗", "？", "?", "哪", "怎么", "为什么"])
        is_short = len(message) < 4
        is_fact = any(kw in message for kw in ["我叫", "我叫", "我是", "喜欢", "住在", "养了", "工作", "生日", "电话", "地址"])
        if is_fact and not is_question and not is_short:
            memory_service.write(user_id=user_id, content=message)
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
