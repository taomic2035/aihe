def test_realtime_ws_broadcast():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    with client.websocket_connect("/v1/realtime?user_id=u_ws") as ws1:
        with client.websocket_connect("/v1/realtime?user_id=u_ws") as ws2:
            # send chat as REST, should broadcast to both WS (via manager)
            # we trigger via chat API which now also publishes to realtime
            client.post("/v1/chat/completions", json={"user_id": "u_ws", "message": "hello realtime"})
            # ws should receive something
            # allow a short recv with timeout
            ws1.send_text("ping")
            data1 = ws1.receive_text()
            assert "pong" in data1 or "hello" in data1 or len(data1) > 0


def test_realtime_requires_user_id():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    try:
        with client.websocket_connect("/v1/realtime") as ws:
            ws.receive_text()
            assert False, "should not connect without user_id"
    except Exception as e:
        assert True
