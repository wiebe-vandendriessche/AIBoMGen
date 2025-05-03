from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Celery app
celery_app = Celery(
    "flower_monitor",
    broker=os.getenv("CELERY_BROKER_URL"),
)

# Minimal configuration for Flower
celery_app.conf.update(
    broker_connection_retry_on_startup=True,
)