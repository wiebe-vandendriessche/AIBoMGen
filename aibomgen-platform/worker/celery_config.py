from celery import Celery
import os
from dotenv import load_dotenv
from kombu import Queue


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
    task_queues=(
        Queue('training_queue', routing_key='training.#'),
    ),
    task_default_queue='training_queue',
    task_default_routing_key='training.default',
    task_time_limit=3600,
    broker_connection_retry_on_startup=True,
    worker_concurrency=1,  # Limit each worker to handle one task at a time
    task_reject_on_worker_lost=True,  # Requeue tasks if a worker crashes
    task_default_retry_delay=60,  # Default delay before retrying a failed task (in seconds)
    task_max_retries=3,  # Maximum number of retries for a task
    result_expires=3600,  # Task results expire after 1 hour
    worker_prefetch_multiplier=1,  # Workers fetch only one task at a time
)


