"""
Celery application configuration.
"""
from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "derbit_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30,
    task_soft_time_limit=25,
)

# Import beat schedule to register periodic tasks
# Import at module level after celery_app is defined
import app.tasks.beat_schedule  # noqa: F401

