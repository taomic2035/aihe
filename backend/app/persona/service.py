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
        rel = self._read("RELATIONSHIP.md")
        # user_profile 来自记忆服务，若未传则读 USER.md 模板
        user = user_profile if user_profile is not None else self._read("USER.md")
        parts = [
            "# SOUL（他的性格）",
            soul,
            "\n# USER（用户画像）",
            user,
            "\n# RELATIONSHIP（关系）",
            rel,
            "\n# 指令",
            "你是 aihe，基于以上 SOUL 与记忆与用户对话。保持温暖、一致、主动关怀。若用户首次对话，需自然披露你是 AI。",
        ]
        return "\n".join(parts)

    def empathy_check(self, draft: str) -> dict:
        """轻量情感校验，首版用规则，未来接 LLM judge"""
        # 简单规则：含温暖词则高分
        warm_words = ["理解", "陪你", "听起来", "能和我说说"]
        score = 3 + sum(1 for w in warm_words if w in draft)
        score = min(5, score)
        return {"score": score, "reason": "warm" if score >= 4 else "cold"}
