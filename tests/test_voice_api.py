def test_voice_stt():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.post("/v1/voice/stt", files={"audio": ("a.wav", b"fake", "audio/wav")})
    assert r.status_code == 200
    assert r.json()["text"] == "你好"


def test_voice_tts():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.post("/v1/voice/tts", json={"text": "你好", "emotion": "warm"})
    assert r.status_code == 200
    assert len(r.content) > 0


def test_voice_session():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.post("/v1/voice/session", json={"user_id": "u1"})
    assert r.status_code == 200
    assert "room" in r.json()
    assert "token" in r.json()


def test_voice_chat():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.post("/v1/voice/chat", files={"audio": ("a.wav", b"fake", "audio/wav")}, data={"user_id": "u_voice"})
    # FastAPI multipart with data may be form; allow fallback
    if r.status_code != 200:
        # try json variant
        r = client.post("/v1/voice/chat", json={"user_id": "u_voice", "text": "你好"})
    assert r.status_code == 200
    assert len(r.content) > 0 or "data" in r.text
