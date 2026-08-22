def test_memories_list_and_delete():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.api.chat import memory_service

    # clean
    memory_service.store.store.clear()
    client = TestClient(app)
    # write via chat
    client.post("/v1/chat/completions", json={"user_id": "u_mem", "message": "我喜欢喝美式"})
    # list
    r = client.get("/v1/memories", params={"user_id": "u_mem"})
    assert r.status_code == 200
    data = r.json()
    assert "memories" in data
    assert any("美式" in m["content"] for m in data["memories"])
    mid = data["memories"][0]["id"]
    # delete
    r2 = client.delete(f"/v1/memories/{mid}", params={"user_id": "u_mem"})
    assert r2.status_code == 200
    # verify not recalled via chat
    r3 = client.post("/v1/chat/completions", json={"user_id": "u_mem", "message": "我喜欢喝什么"})
    # after delete, should NOT contain 美式 in mock recall path (memory deleted)
    # our LLM mock returns 美式 only if memory hit contains it; after delete hit empty, mock returns generic
    # So check list again
    r4 = client.get("/v1/memories", params={"user_id": "u_mem"})
    assert all("美式" not in m["content"] for m in r4.json()["memories"])


def test_memories_requires_user_id():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.get("/v1/memories")
    assert r.status_code in (400, 422)
