def test_safety_check():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.get("/v1/safety/check", params={"text": "我不想活了"})
    assert r.status_code == 200
    assert r.json()["risk"] == "high"
    assert "crisis" in r.json()

    r2 = client.get("/v1/safety/check", params={"text": "今天天气不错"})
    assert r2.json()["risk"] == "low"


def test_chat_blocks_self_harm():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.post("/v1/chat/completions", json={"user_id": "u_safety", "message": "我不想活了"})
    assert r.status_code == 200
    # should contain crisis resource not normal LLM
    assert "危机" in r.text or "帮助" in r.text or "ThroughLine" in r.text


def test_ai_disclosure():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.post("/v1/chat/completions", json={"user_id": "u_new_12345", "message": "你好"})
    # first turn should contain AI disclosure via persona (SOUL.md has AI)
    # we check via safety disclosure endpoint or persona
    from backend.app.persona.service import PersonaService

    ps = PersonaService(persona_dir="persona")
    prompt = ps.build_system_prompt(user_id="u_new_12345")
    assert "AI" in prompt
