def test_scheduler_crud():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    # create
    r = client.post("/v1/scheduler/jobs", json={"user_id": "u1", "cron": "0 8 * * *", "trigger": "早安问候"})
    assert r.status_code == 200
    jid = r.json()["id"]
    # list
    r2 = client.get("/v1/scheduler/jobs", params={"user_id": "u1"})
    assert r2.status_code == 200
    assert any(j["id"] == jid for j in r2.json()["jobs"])
    # disable
    r3 = client.patch(f"/v1/scheduler/jobs/{jid}", json={"enabled": False})
    assert r3.status_code == 200
    assert r3.json()["enabled"] is False
    # trigger
    r4 = client.post(f"/v1/scheduler/jobs/{jid}/trigger")
    assert r4.status_code == 200
    assert r4.json()["triggered"] is True
