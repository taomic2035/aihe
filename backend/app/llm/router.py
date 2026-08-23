import time
from typing import Iterable

from backend.app.observability.langfuse import log_generation


class LLMRouter:
    def __init__(self, api_key: str = "dummy", base_url: str = "https://openrouter.ai/api/v1", model: str = "qwen/qwen3-32b"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.last_prompt: str = ""

    def _build_prompt(self, persona_prompt: str, memories: list[str], message: str) -> str:
        mem_str = "\n".join(f"- {m}" for m in memories) if memories else "(无相关记忆)"
        prompt = f"""{persona_prompt}

# 相关记忆
{mem_str}

# 用户消息
{message}
"""
        self.last_prompt = prompt
        return prompt

    def stream(self, user_id: str, message: str, persona_prompt: str, memories: list[str]) -> Iterable[str]:
        prompt = self._build_prompt(persona_prompt, memories, message)
        if self.base_url.startswith("memory://"):
            if "error" in self.base_url:
                yield "抱歉，我刚刚走神了，能再说一遍吗？"
                return
            if any("美式" in m for m in memories):
                yield "你喜欢喝美式"
                yield "，我记得你在上海"
                return
            yield f"收到：{message}（mock 回复，persona 已注入）"
            return

        t0 = time.perf_counter()
        full_reply = ""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": persona_prompt}, {"role": "user", "content": f"记忆:{memories}\n消息:{message}"}],
                stream=True,
            )
            for chunk in resp:
                if chunk.choices[0].delta.content:
                    c = chunk.choices[0].delta.content
                    full_reply += c
                    yield c
        except Exception as e:
            full_reply = f"（降级回复）{message[:20]}..."
            yield full_reply

        duration_ms = (time.perf_counter() - t0) * 1000
        log_generation(
            name="llm.chat",
            input_data={"user_id": user_id, "message": message, "model": self.model},
            output_data={"reply_len": len(full_reply)},
            model=self.model,
            duration_ms=duration_ms,
        )
