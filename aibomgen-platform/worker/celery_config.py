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

# Celery configuration
celery_app.conf.update(
    task_routes={
        'tasks.run_training': {'queue': 'training_queue'},
    },
    task_queues=(
        Queue('training_queue', routing_key='training.#'),
    ),
    task_default_queue='training_queue',
    task_default_routing_key='training.default',
    task_time_limit=3600,  # Maximum time a task can run (in seconds)
    # Retry connecting to the broker on startup
    broker_connection_retry_on_startup=True,
    worker_concurrency=1,  # Limit each worker to handle one task at a time
    task_reject_on_worker_lost=True,  # Requeue tasks if a worker crashes
    # Default delay before retrying a failed task (in seconds)
    task_default_retry_delay=60,
    task_max_retries=3,  # Maximum number of retries for a task
    result_persistent=True,  # Make result messages persistent
    result_expires=None,  # Results won't expire automatically
    worker_prefetch_multiplier=1,  # Workers fetch only one task at a time
    accept_content=["json"],  # Accept only JSON-serialized tasks
    task_serializer="json",  # Serialize tasks as JSON
    result_serializer="json",  # Serialize results as JSON
    timezone="UTC",  # Set timezone to UTC
    enable_utc=True,  # Enable UTC timezone
    database_create_tables_at_setup=True,  # Automatically create tables at setup
    # Enable verbose SQLAlchemy logging (optional)
    database_engine_options={"echo": True},
    database_table_names={  # Customize table names (optional)
        "task": "celery_taskmeta",
        "group": "celery_groupmeta",
    },
    result_backend=os.getenv("CELERY_RESULT_BACKEND"),
    result_extended=True,  # Extend the result backend with additional fields
)
