def test_tools_registry_and_api():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    # calendar
    r = client.post("/v1/tools/call", json={"tool": "calendar", "args": {"user_id": "u1", "date": "2026-08-22"}})
    assert r.status_code == 200
    assert "events" in r.json() or "result" in r.json()

    # search
    r2 = client.post("/v1/tools/call", json={"tool": "search", "args": {"query": "天气"}})
    assert r2.status_code == 200
    assert "mock result" in str(r2.json()).lower() or "result" in r2.json()

    # memo
    r3 = client.post("/v1/tools/call", json={"tool": "memo", "args": {"user_id": "u1", "content": "记得买牛奶"}})
    assert r3.status_code == 200
    assert r3.json().get("ok") is True

    # list tools
    r4 = client.get("/v1/tools/list")
    assert r4.status_code == 200
    assert len(r4.json()["tools"]) >= 3
