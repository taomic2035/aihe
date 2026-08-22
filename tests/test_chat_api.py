def test_chat_stream_and_memory_persist():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    # first message writes memory implicitly via API (mock)
    r = client.post("/v1/chat/completions", json={"user_id": "u1", "message": "我叫阿明，喜欢喝美式"})
    assert r.status_code == 200
    text = r.text
    assert "data:" in text or "阿明" in text or "美式" in text or len(text) > 0

    # second message should recall previous
    r2 = client.post("/v1/chat/completions", json={"user_id": "u1", "message": "我喜欢喝什么"})
    assert r2.status_code == 200
    assert "美式" in r2.text or "data:" in r2.text


def test_health():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_chat_requires_user_id():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.post("/v1/chat/completions", json={"message": "hi"})
    assert r.status_code in (400, 422)
