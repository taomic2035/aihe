from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import json

from backend.app.persona.service import PersonaService
from backend.app.memory.service import MemoryService
from backend.app.llm.router import LLMRouter
from backend.app.observability.langfuse import log_trace

router = APIRouter()

# Singletons for TDD (in production would be DI)
persona_service = PersonaService(persona_dir="persona")
memory_service = MemoryService(qdrant_url="memory://test", letta_url="memory://test")
llm_router = LLMRouter(api_key="dummy", base_url="memory://test")


class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: str | None = None


@router.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    user_id = req.user_id
    message = req.message

    # 1. recall
    hits = memory_service.recall(user_id=user_id, query=message, limit=8)
    mem_texts = [h.content for h in hits]
    log_trace("memory.recall", {"user_id": user_id, "query": message, "hits": len(hits)})

    # 2. persona
    persona_prompt = persona_service.build_system_prompt(user_id=user_id)
    log_trace("chat.completions", {"user_id": user_id, "message": message, "memories": mem_texts})

    # 3. stream via LLM
    def generate():
        # SSE format
        for chunk in llm_router.stream(user_id=user_id, message=message, persona_prompt=persona_prompt, memories=mem_texts):
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        # persist memory after stream (very naive: if message contains "我叫" or "喜欢" then store)
        # keep it simple for TDD: store user message as memory if it looks like a fact
        if any(kw in message for kw in ["我叫", "喜欢", "住在", "养", "叫"]):
            memory_service.write(user_id=user_id, content=message)
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
