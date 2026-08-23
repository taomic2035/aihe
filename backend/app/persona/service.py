import pathlib


class PersonaService:
    def __init__(self, persona_dir: str = "persona"):
        self.dir = pathlib.Path(persona_dir)

    def _read(self, name: str) -> str:
        p = self.dir / name
        if p.exists():
            return p.read_text(encoding="utf-8")
        return ""

    def build_system_prompt(self, user_id: str, user_profile: str | None = None) -> str:
        soul = self._read("SOUL.md")
        parts = [
            "# SOUL",
            soul,
            "\n# 指令",
            "你是 aihe，按 SOUL 与用户对话。核心：简洁、2-3句、不啰嗦、不重复、不用套话。根据用户消息的长度和情绪调节回复长度。",
        ]
        return "\n".join(parts)

    def empathy_check(self, draft: str) -> dict:
        """轻量情感校验，首版用规则，未来接 LLM judge"""
        # 简单规则：含温暖词则高分
        warm_words = ["理解", "陪你", "听起来", "能和我说说"]
        score = 3 + sum(1 for w in warm_words if w in draft)
        score = min(5, score)
        return {"score": score, "reason": "warm" if score >= 4 else "cold"}
