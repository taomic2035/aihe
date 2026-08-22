import asyncio


def test_router_streams_with_persona_and_memory():
    from backend.app.llm.router import LLMRouter

    router = LLMRouter(api_key="dummy", base_url="memory://test")
    # mock memory hits
    memories = ["我喜欢喝美式"]
    persona = "你是 aihe，温暖的陪伴"
    chunks = list(router.stream(user_id="u1", message="我喜欢喝什么", persona_prompt=persona, memories=memories))
    assert len(chunks) > 0
    text = "".join(chunks)
    assert len(text) > 0
    # should have seen persona/memories in prompt (checked via router.last_prompt)
    assert "美式" in router.last_prompt or "aihe" in router.last_prompt


def test_router_fallback_on_error():
    from backend.app.llm.router import LLMRouter

    router = LLMRouter(api_key="dummy", base_url="memory://error")
    # should not raise, should fallback to dummy response
    chunks = list(router.stream(user_id="u1", message="hi", persona_prompt="p", memories=[]))
    assert len(chunks) > 0
