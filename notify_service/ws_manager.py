from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(
            f"✅ User {user_id} connected. Total connections: \
            {len(self.active_connections)}"
        )

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        print(
            f"❌ User {user_id} disconnected. Total connections: \
            {len(self.active_connections)}"
        )

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(message)
        else:
            print(f"⚠️ User {user_id} not found in active connections")


manager = ConnectionManager()
