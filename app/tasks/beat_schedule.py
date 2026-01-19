"""
Celery beat schedule configuration.
"""
from app.tasks.celery_app import celery_app

# Configure periodic task schedule
celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "fetch_and_save_prices",
        "schedule": 60.0,  # Run every 60 seconds (1 minute)
    },
}

