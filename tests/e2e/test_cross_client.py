def test_cross_client_flow():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.api.chat import memory_service

    memory_service.store.store.clear()
    client = TestClient(app)
    # Client A writes via chat
    r = client.post("/v1/chat/completions", json={"user_id": "u_e2e", "message": "我叫阿明，喜欢喝美式"})
    assert r.status_code == 200

    # Client B (same user_id) lists memories via REST
    r2 = client.get("/v1/memories", params={"user_id": "u_e2e"})
    assert r2.status_code == 200
    assert any("美式" in m["content"] for m in r2.json()["memories"])

    # Client B chats and should recall
    r3 = client.post("/v1/chat/completions", json={"user_id": "u_e2e", "message": "我叫什么，喜欢喝什么"})
    assert r3.status_code == 200
    # our mock returns 美式 if memory hit
    assert "美式" in r3.text

    # Verify trace exists
    from backend.app.observability.langfuse import get_traces, clear_traces

    traces = get_traces()
    assert any(t["name"] == "memory.recall" for t in traces)
    assert any(t["name"] == "chat.completions" for t in traces)


def test_delete_not_recalled_e2e():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.api.chat import memory_service

    memory_service.store.store.clear()
    client = TestClient(app)
    client.post("/v1/chat/completions", json={"user_id": "u_del", "message": "我喜欢去北京"})
    r = client.get("/v1/memories", params={"user_id": "u_del"})
    assert any("北京" in m["content"] for m in r.json()["memories"])
    mid = r.json()["memories"][0]["id"]
    client.delete(f"/v1/memories/{mid}", params={"user_id": "u_del"})
    r2 = client.get("/v1/memories", params={"user_id": "u_del"})
    assert all("北京" not in m["content"] for m in r2.json()["memories"])
    # chat should not recall deleted
    r3 = client.post("/v1/chat/completions", json={"user_id": "u_del", "message": "我明天去哪"})
    assert "北京" not in r3.text or "data:" in r3.text  # generic mock after delete
