from celery import Celery

celery_app = Celery(
    "aibomgen_worker",
    broker="redis://redis:6379/0",  # Redis broker
    backend="redis://redis:6379/0",  # Redis backend to track task results
)

celery_app.conf.update(
    task_routes={
        'tasks.run_training': {'queue': 'training_queue'},
    },
    task_time_limit=3600,
    broker_connection_retry_on_startup=True
)
