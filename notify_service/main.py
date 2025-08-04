import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .consumer import consumer
from .ws_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(consumer.start())
    print("✅ Notificação: consumidor iniciado.")
    yield
    print("🛑 Finalizando app...")
    consumer_task.cancel()


app = FastAPI(title="Serviço de Notificações", lifespan=lifespan)


@app.websocket('/ws/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print(f"🔗 WebSocket connection attempt from {user_id}")
    await manager.connect(user_id, websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            print(f"📨 Received from {user_id}: {msg}")

            if msg == "ready":
                await websocket.send_text("connected")
            elif msg == "keepalive":
                await websocket.send_text("alive")

    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected for {user_id}")
        manager.disconnect(user_id)
    except Exception as e:
        print(f"❌ Error in WebSocket for {user_id}: {e}")
        manager.disconnect(user_id)
