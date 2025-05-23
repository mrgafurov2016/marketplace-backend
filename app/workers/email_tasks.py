from app.celery_worker import celery_app
import time

@celery_app.task
def send_email_task(to_email: str, subject: str, body: str):
    # Тут можно использовать smtplib или сервис вроде SendGrid
    print(f"Sending email to {to_email} with subject '{subject}'")
    time.sleep(2)  # симуляция задержки
    print("Email sent.")
