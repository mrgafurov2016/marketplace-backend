from celery import Celery

celery_app = Celery(
    "worker",
    broker="amqp://guest:guest@rabbitmq:5672//",  # <--- тут ключевое изменение
    backend="rpc://"
)

celery_app.conf.task_routes = {
    "app.workers.email_tasks.send_email_task": {"queue": "emails"},
}