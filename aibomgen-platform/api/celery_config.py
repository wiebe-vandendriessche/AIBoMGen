import os
from celery import Celery

celery_app = Celery(
    "aibomgen_worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery_app.conf.update(
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
)
