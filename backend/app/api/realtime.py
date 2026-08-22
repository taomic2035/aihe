from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.app.realtime.manager import manager

router = APIRouter()


@router.websocket("/v1/realtime")
async def realtime_ws(websocket: WebSocket, user_id: str | None = Query(default=None)):
    if not user_id:
        await websocket.close(code=1008, reason="user_id required")
        return
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # echo + broadcast
            if data == "ping":
                await websocket.send_text("pong")
            else:
                await manager.broadcast(user_id, data)
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
