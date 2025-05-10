#!/bin/bash

# Dynamically set the worker name using the Docker Swarm task slot
WORKER_NAME="worker_${HOSTNAME}"

# Start the Celery worker with the dynamically generated name
celery -A tasks worker --loglevel=info -n "$WORKER_NAME" --queues=training_queue