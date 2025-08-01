import json
import logging
import os

import pika
from dotenv import load_dotenv

from email_sender import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


class RabbitmqConsumer:
    def __init__(self) -> None:
        self.__host = os.getenv("RABBITMQ_HOST", "localhost")
        self.__port = int(os.getenv("RABBITMQ_PORT", 5672))
        self.__username = os.getenv("RABBITMQ_USER", "guest")
        self.__password = os.getenv("RABBITMQ_PASS", "guest")
        self.__queue = "notifier"
        self.__connection = None
        self.__channel = self.__create_channel()

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            credentials=pika.PlainCredentials(self.__username, self.__password)
        )

        self.__connection = pika.BlockingConnection(connection_parameters)
        channel = self.__connection.channel()

        channel.queue_declare(queue=self.__queue, durable=True)

        channel.basic_consume(
            queue=self.__queue,
            auto_ack=True,
            on_message_callback=self.callback_wrapper
        )

        return channel

    def callback_wrapper(self, ch, method, properties, body):
        try:
            data = json.loads(body.decode())
            title = data.get("title")
            email = data.get("email")
            time_notify = data.get("notify_at")

            if not title or not email or not time_notify:
                logger.warning("Mensagem recebida sem os campos necessários: %s", data)
                return

            message = (
                "⚠️ Atenção!\n\n"
                f"Você tem apenas {time_notify} restantes para finalizar a tarefa:\n\n"
                f"📌 {title}\n\n"
                "Não perca o prazo!"
            )

            logger.info(f"Mensagem recebida: title={title}, email={email}")
            send_email(subject='Vencimento de Task', to_email=email, body=message)

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar mensagem: {e}")
        except Exception as e:
            logger.exception(f"Erro ao processar a mensagem: {e}")

    def start(self):
        logger.info("Iniciando consumidor RabbitMQ na fila 'notifier'...")
        self.__channel.start_consuming()

    def close(self):
        if self.__connection and self.__connection.is_open:
            self.__connection.close()


if __name__ == "__main__":
    consumer = RabbitmqConsumer()
    try:
        consumer.start()
    except KeyboardInterrupt:
        consumer.close()
        logger.info("Consumidor finalizado manualmente.")
