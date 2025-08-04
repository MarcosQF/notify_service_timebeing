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
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
