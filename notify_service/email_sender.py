import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def send_email(subject: str, body: str, to_email: str):
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    from_email = settings.EMAIL_USER
    from_password = settings.EMAIL_PASS

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, from_password)
            server.send_message(message)
            logger.info(f"E-mail enviado para {to_email}")
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail para {to_email}: {e}")
