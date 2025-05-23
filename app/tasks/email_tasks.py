from celery import Celery
import smtplib
from email.mime.text import MIMEText
from app.config import settings

celery = Celery(__name__, broker="amqp://guest:guest@rabbitmq:5672//")

@celery.task
def send_registration_email(to_email: str):
    msg = MIMEText("Вы успешно зарегистрировались в Marketplace!")
    msg["Subject"] = "Добро пожаловать!"
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")