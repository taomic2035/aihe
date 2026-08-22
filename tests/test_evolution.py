def test_evolution_run():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    r = client.post("/v1/evolution/run", json={"user_id": "u1"})
    assert r.status_code == 200
    data = r.json()
    assert "pr_url" in data
    assert "score" in data
    assert data["score"] >= 0
    # gate: size <=15KB
    assert len(data.get("variant", "")) <= 15 * 1024

    r2 = client.get("/v1/evolution/prs")
    assert r2.status_code == 200
    assert "prs" in r2.json()
