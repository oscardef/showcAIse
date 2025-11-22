import redis
from celery import Celery
from .config import get_settings

settings = get_settings()

# Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Celery app
celery_app = Celery(
    "showcaise",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
