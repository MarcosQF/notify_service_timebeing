import asyncio
import json
import logging

from aio_pika import IncomingMessage, connect_robust

from .database import get_session
from .email_sender import send_email
from .models import Notification
from .settings import settings
from .ws_manager import manager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class AsyncRabbitmqConsumer:
    def __init__(self):
        self.__host = settings.RABBITMQ_HOST
        self.__port = settings.RABBITMQ_PORT
        self.__username = settings.RABBITMQ_USER
        self.__password = settings.RABBITMQ_PASS
        self.__queue = "notifier"
        self.__connection = None
        self.__channel = None
        self.__consumer_tag = None

    async def connect(self):
        self.__connection = await connect_robust(
            host=self.__host,
            port=self.__port,
            login=self.__username,
            password=self.__password,
        )
        self.__channel = await self.__connection.channel()
        await self.__channel.set_qos(prefetch_count=1)
        queue = await self.__channel.declare_queue(self.__queue, durable=True)
        self.__consumer_tag = await queue.consume(self.on_message)

        logger.info(
            "Conectado ao RabbitMQ e consumidor iniciado na fila '%s'.", self.__queue
        )

    async def on_message(self, message: IncomingMessage):
        async with message.process():
            try:
                data = json.loads(message.body.decode())
                title = data.get("title")
                email = data.get("email")
                time_notify = data.get("notify_at")

                if not title or not email or not time_notify:
                    logger.warning(
                        "Mensagem recebida sem os campos necessários: %s", data
                    )
                    return

                msg = (
                    "⚠️ Atenção!\n\n"
                    f"Você tem apenas {time_notify}\
                    restantes para finalizar a tarefa:\n\n"
                    f"📌 {title}\n\n"
                    "Não perca o prazo!"
                )

                logger.info(f"Mensagem recebida: title={title}, email={email}")
                send_email(subject="Vencimento de Task", to_email=email, body=msg)

                await manager.send_personal_message(
                    message=msg,
                    user_id=email,
                    level="info",
                    title="⏰ Tarefa próxima do vencimento!"
                )

                session = get_session()
                try:
                    db_notification = Notification(
                        email=email, task_title=title, notify_at=time_notify
                    )
                    session.add(db_notification)
                    session.commit()
                    session.refresh(db_notification)
                except Exception:
                    session.rollback()
                    raise
                finally:
                    session.close()

            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar mensagem: {e}")
            except Exception as e:
                logger.exception(f"Erro ao processar a mensagem: {e}")

    async def start(self):
        await self.connect()
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Consumidor cancelado, fechando conexão...")
            await self.close()

    async def close(self):
        if self.__connection:
            await self.__connection.close()
            logger.info("Conexão RabbitMQ fechada.")


consumer = AsyncRabbitmqConsumer()
