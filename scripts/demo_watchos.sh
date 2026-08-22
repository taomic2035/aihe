#!/bin/bash
set -e
echo "=== WatchOS thin demo (curl mock) ==="
python3 -m pytest tests/test_watch.py -v
echo "--- curl sync ---"
python3 -c "from fastapi.testclient import TestClient; from backend.app.main import app; c=TestClient(app); c.post('/v1/chat/completions', json={'user_id':'watch_demo','message':'我叫阿明，喜欢喝美式'}); print(c.get('/v1/watch/sync', params={'user_id':'watch_demo','since_version':0}).json())"
echo "--- evolution PR file ---"
python3 -c "from fastapi.testclient import TestClient; from backend.app.main import app; c=TestClient(app); print(c.post('/v1/evolution/run', json={'user_id':'watch_demo'}).json()); import pathlib, glob; print(glob.glob('evolution/prs/*.md')[:2])"
