#!/bin/bash
set -e
echo "=== aihe Phase C Demo ==="
echo "1. docker compose config check"
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml')); print('compose ok')"
echo "2. pytest"
python3 -m pytest -q
echo "3. health"
python3 -c "from fastapi.testclient import TestClient; from backend.app.main import app; c=TestClient(app); print(c.get('/health').json())"
echo "4. chat demo"
python3 <<'PY'
from fastapi.testclient import TestClient
from backend.app.main import app
c=TestClient(app)
r=c.post("/v1/chat/completions", json={"user_id":"demo","message":"我叫阿明，喜欢喝美式"})
print("chat1:", r.text[:200])
r=c.post("/v1/chat/completions", json={"user_id":"demo","message":"我喜欢喝什么"})
print("chat2 recall:", r.text[:300])
r=c.get("/v1/memories", params={"user_id":"demo"})
print("memories:", r.json())
PY
echo "=== demo done ==="
