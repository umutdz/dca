from celery import Celery
from app.core.config import config

# Initialize Celery
celery_app = Celery(
    "chat_assistant",
    broker=f"amqp://{config.RABBITMQ_DEFAULT_USER}:{config.RABBITMQ_DEFAULT_PASS}@{config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}//",
    backend=f"db+postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}",
    include=["app.tasks.tasks"],
)

# Configure Celery
env_suffix = config.APP_ENV.lower()
celery_app.conf.update(
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
    task_ignore_result=False,
    result_extended=True,
    result_serializer="json",
    task_serializer="json",
    accept_content=["json"],
    task_routes={
        # "task-name": {"queue": f"{queue_prefix}_{env_suffix}"},
    },
)
