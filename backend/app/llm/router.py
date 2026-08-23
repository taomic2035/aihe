import time
from typing import Iterable
from collections import defaultdict

from backend.app.observability.langfuse import log_generation


class LLMRouter:
    def __init__(self, api_key: str = "dummy", base_url: str = "https://openrouter.ai/api/v1", model: str = "qwen/qwen3-32b"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.last_prompt: str = ""
        self._history: dict[str, list[dict]] = defaultdict(list)
        self._max_history = 10

    def _build_messages(self, persona_prompt: str, memories: list[str], message: str, user_id: str) -> list[dict]:
        msgs = [{"role": "system", "content": persona_prompt}]
        if memories:
            mem_str = "\n".join(f"- {m}" for m in memories)
            msgs.append({"role": "system", "content": f"相关记忆:\n{mem_str}"})
        for h in self._history.get(user_id, []):
            msgs.append(h)
        msgs.append({"role": "user", "content": message})
        return msgs

    def stream(self, user_id: str, message: str, persona_prompt: str, memories: list[str]) -> Iterable[str]:
        msgs = self._build_messages(persona_prompt, memories, message, user_id)
        self.last_prompt = "\n".join(m["content"][:80] for m in msgs)

        full_reply = ""
        if self.base_url.startswith("memory://"):
            if "error" in self.base_url:
                full_reply = "抱歉，我刚刚走神了，能再说一遍吗？"
            elif any("美式" in m for m in memories):
                full_reply = "你喜欢喝美式，我记得你在上海"
            else:
                full_reply = f"收到：{message}（mock 回复，persona 已注入）"
            yield full_reply
        else:
            t0 = time.perf_counter()
            try:
                from openai import OpenAI

                client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                resp = client.chat.completions.create(
                    model=self.model,
                    messages=msgs,
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

        hist = self._history[user_id]
        hist.append({"role": "user", "content": message})
        hist.append({"role": "assistant", "content": full_reply})
        if len(hist) > self._max_history * 2:
            self._history[user_id] = hist[-(self._max_history * 2):]
