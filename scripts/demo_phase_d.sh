#!/bin/bash
set -e
echo "=== Phase D Demo ==="
python3 -m pytest -q
echo "--- voice ---"
python3 -c "from fastapi.testclient import TestClient; from backend.app.main import app; c=TestClient(app); print(c.post('/v1/voice/stt', files={'audio':('a.wav', b'fake','audio/wav')}).json()); print('tts len', len(c.post('/v1/voice/tts', json={'text':'你好','emotion':'warm'}).content))"
echo "--- watch ---"
python3 -c "from fastapi.testclient import TestClient; from backend.app.main import app; c=TestClient(app); print(c.get('/v1/watch/sync', params={'user_id':'demo','since_version':0}).json())"
echo "--- tools ---"
python3 -c "from fastapi.testclient import TestClient; from backend.app.main import app; c=TestClient(app); print(c.post('/v1/tools/call', json={'tool':'search','args':{'query':'天气'}}).json())"
echo "--- evolution ---"
python3 -c "from fastapi.testclient import TestClient; from backend.app.main import app; c=TestClient(app); print(c.post('/v1/evolution/run', json={'user_id':'demo'}).json())"
echo "--- safety ---"
python3 -c "from fastapi.testclient import TestClient; from backend.app.main import app; c=TestClient(app); print(c.get('/v1/safety/check', params={'text':'我不想活了'}).json())"
echo "=== all done ==="
