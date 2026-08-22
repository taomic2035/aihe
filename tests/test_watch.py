def test_watch_sync_and_push():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.api.chat import memory_service

    memory_service.store.store.clear()
    client = TestClient(app)
    client.post("/v1/chat/completions", json={"user_id": "u_watch", "message": "我叫阿明，喜欢喝美式"})
    r = client.get("/v1/watch/sync", params={"user_id": "u_watch", "since_version": 0})
    assert r.status_code == 200
    assert "messages" in r.json() or "memories" in r.json()
    assert r.json()["version"] >= 1

    r2 = client.post("/v1/watch/push", json={"user_id": "u_watch", "title": "提醒", "body": "喝水"})
    assert r2.status_code == 200

    r3 = client.post("/v1/watch/ingest", json={"user_id": "u_watch", "heart_rate": 72, "sleep": 7.5})
    assert r3.status_code == 200


def test_watch_requires_user_id():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.get("/v1/watch/sync")
    assert r.status_code in (400, 422)
