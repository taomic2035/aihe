from collections import defaultdict


class RealtimeManager:
    def __init__(self):
        self.connections: dict[str, list] = defaultdict(list)

    async def connect(self, user_id: str, ws):
        await ws.accept()
        self.connections[user_id].append(ws)

    def disconnect(self, user_id: str, ws):
        if ws in self.connections[user_id]:
            self.connections[user_id].remove(ws)

    async def broadcast(self, user_id: str, message: str):
        for ws in list(self.connections[user_id]):
            try:
                await ws.send_text(message)
            except Exception:
                pass


manager = RealtimeManager()
