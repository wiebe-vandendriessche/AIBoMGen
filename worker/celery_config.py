from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "aibomgen_worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery_app.conf.update(
    task_routes={
        'tasks.run_training': {'queue': 'training_queue'},
    },
    task_time_limit=3600,
    broker_connection_retry_on_startup=True
)
