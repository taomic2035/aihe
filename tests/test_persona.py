def test_persona_injection():
    from backend.app.persona.service import PersonaService

    svc = PersonaService(persona_dir="persona")
    prompt = svc.build_system_prompt(user_id="u1")
    assert "SOUL" in prompt or "性格" in prompt or "温暖" in prompt
    assert len(prompt) > 100


def test_persona_has_soul_file():
    import pathlib

    assert pathlib.Path("persona/SOUL.md").exists()
    content = pathlib.Path("persona/SOUL.md").read_text()
    assert len(content) > 50
    # must mention AI identity disclosure
    assert "AI" in content or "人工智能" in content
