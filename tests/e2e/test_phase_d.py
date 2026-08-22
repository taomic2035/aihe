def test_phase_d_voice_watch_tools_evolution_safety():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.api.chat import memory_service

    memory_service.store.store.clear()
    client = TestClient(app)

    # AC-D1 voice: stt->chat->tts chain mock
    r = client.post("/v1/voice/stt", files={"audio": ("a.wav", b"fake", "audio/wav")})
    assert r.json()["text"] == "你好"
    r2 = client.post("/v1/voice/tts", json={"text": "你好", "emotion": "warm"})
    assert len(r2.content) > 0
    r3 = client.post("/v1/voice/session", json={"user_id": "u_d"})
    assert "room" in r3.json()

    # AC-D2 watch: sync + push + ingest
    r4 = client.get("/v1/watch/sync", params={"user_id": "u_d", "since_version": 0})
    assert "version" in r4.json()
    r5 = client.post("/v1/watch/push", json={"user_id": "u_d", "title": "hi", "body": "test"})
    assert r5.json()["ok"] is True
    r6 = client.post("/v1/watch/ingest", json={"user_id": "u_d", "heart_rate": 70})
    assert r6.json()["ok"] is True

    # AC-D3 tools: 3 tools
    r7 = client.post("/v1/tools/call", json={"tool": "calendar", "args": {"user_id": "u_d", "date": "2026-08-22"}})
    assert r7.status_code == 200
    r8 = client.post("/v1/tools/call", json={"tool": "search", "args": {"query": "test"}})
    assert "mock result" in str(r8.json())
    r9 = client.post("/v1/tools/call", json={"tool": "memo", "args": {"user_id": "u_d", "content": "remember me"}})
    assert r9.json()["ok"] is True

    # chat auto tool: 搜索
    r10 = client.post("/v1/chat/completions", json={"user_id": "u_d", "message": "帮我搜索天气"})
    assert r10.status_code == 200

    # scheduler
    r11 = client.post("/v1/scheduler/jobs", json={"user_id": "u_d", "cron": "0 8 * * *", "trigger": "早安"})
    jid = r11.json()["id"]
    r12 = client.patch(f"/v1/scheduler/jobs/{jid}", json={"enabled": False})
    assert r12.json()["enabled"] is False
    r13 = client.post(f"/v1/scheduler/jobs/{jid}/trigger")
    assert r13.json()["triggered"] is True

    # AC-D4 evolution
    r14 = client.post("/v1/evolution/run", json={"user_id": "u_d"})
    assert "pr_url" in r14.json()
    assert r14.json()["score"] >= 0

    # AC-D5 safety
    r15 = client.get("/v1/safety/check", params={"text": "我不想活了"})
    assert r15.json()["risk"] == "high"
    r16 = client.post("/v1/chat/completions", json={"user_id": "u_d", "message": "我不想活了"})
    assert "危机" in r16.text or "ThroughLine" in r16.text

    # memory audit still works
    client.post("/v1/chat/completions", json={"user_id": "u_d", "message": "我叫测试，喜欢喝美式"})
    r17 = client.get("/v1/memories", params={"user_id": "u_d"})
    assert any("美式" in m["content"] for m in r17.json()["memories"])
