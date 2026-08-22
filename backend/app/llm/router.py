from typing import Iterable


class LLMRouter:
    """
    OpenRouter 统一入口。
    memory://test 走本地 mock，无需真实 API key，便于 TDD。
    """

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
        # memory:// 协议走 mock，避免真实调用
        if self.base_url.startswith("memory://"):
            # fallback 逻辑：若 base_url 含 error 则走降级分支
            if "error" in self.base_url:
                yield "抱歉，我刚刚走神了，能再说一遍吗？"
                return
            # 简单 mock：若记忆含美式则回答美式
            if any("美式" in m for m in memories):
                yield "你喜欢喝美式"
                yield "，我记得你在上海"
                return
            yield f"收到：{message}（mock 回复，persona 已注入）"
            return

        # 真实 OpenRouter 调用（此分支 TDD 阶段不走到，保留实现骨架）
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
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"（降级回复）{message[:20]}..."
