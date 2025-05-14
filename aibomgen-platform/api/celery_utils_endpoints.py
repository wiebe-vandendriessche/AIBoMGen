from typing import Dict, List
from fastapi import APIRouter, Depends
from celery_config import celery_app
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Job
from celery.result import AsyncResult
# Import the get_current_user dependency
from auth_utils import get_current_user

# Dependency to get a database session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


celery_utils_router = APIRouter(
    prefix="/celery_utils", tags=["Celery utils Endpoints"])


@celery_utils_router.get("/tasks", response_model=List[Dict])
async def get_all_tasks(db: Session = Depends(get_db)):
    """
    Returns all tasks (finished, failed, or pending) using AsyncResult.
    """
    tasks = []

    # Collect task IDs from the database
    task_ids = [job.id for job in db.query(Job).all()]

    # Add all tasks using AsyncResult
    for task_id in task_ids:
        async_result = AsyncResult(task_id, app=celery_app)
        tasks.append({
            "id": task_id,
            "name": async_result.name,
            "state": async_result.state,
            "result": async_result.result if async_result.state == "SUCCESS" else None,
            "traceback": async_result.traceback if async_result.state == "FAILURE" else None,
        })

    return tasks


@celery_utils_router.get("/tasks/running", response_model=List[Dict])
async def get_running_tasks(db: Session = Depends(get_db)):
    """
    Returns all currently running tasks in detail using query_results.
    """
    i = celery_app.control.inspect()  # Use Inspect class
    tasks = []

    if i:
        # Collect task IDs from the database
        task_ids = [job.id for job in db.query(Job).all()]

        # Use Inspect's query_task method
        query_results = i.query_task(*task_ids) if task_ids else None
        if query_results:  # Ensure query_results is not None
            for worker, worker_tasks in query_results.items():
                for task_id, task_data in worker_tasks.items():
                    state, task_info = task_data
                    tasks.append({
                        "id": task_info["id"],
                        "name": task_info["name"],
                        "state": state,
                        "worker": worker,
                        "args": task_info.get("args", []),
                        "kwargs": task_info.get("kwargs", {}),
                        "type": task_info["type"],
                        "hostname": task_info["hostname"],
                        "time_start": task_info.get("time_start"),
                        "acknowledged": task_info.get("acknowledged"),
                        "delivery_info": task_info.get("delivery_info", {}),
                        "worker_pid": task_info.get("worker_pid"),
                    })

    return tasks


@celery_utils_router.get("/tasks/my", response_model=List[Dict])
async def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns all tasks (finished, failed, or pending) for the current user using AsyncResult.
    """
    tasks = []

    # Collect task IDs from the database for the current user
    task_ids = [job.id for job in db.query(Job).filter(
        Job.user_id == current_user.claims["oid"]).all()]

    # Add all tasks using AsyncResult
    for task_id in task_ids:
        async_result = AsyncResult(task_id, app=celery_app)
        tasks.append({
            "id": task_id,
            "name": async_result.name,
            "state": async_result.state,
            "result": async_result.result if async_result.state == "SUCCESS" else None,
            "traceback": async_result.traceback if async_result.state == "FAILURE" else None,
        })

    return tasks


@celery_utils_router.get("/tasks/running/my", response_model=List[Dict])
async def get_my_running_tasks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns all currently running tasks in detail for the current user using query_results.
    """
    i = celery_app.control.inspect()  # Use Inspect class
    tasks = []

    if i:
        # Collect task IDs from the database for the current user
        task_ids = [job.id for job in db.query(Job).filter(
            Job.user_id == current_user.claims["oid"]).all()]

        # Use Inspect's query_task method
        query_results = i.query_task(*task_ids) if task_ids else None
        if query_results:  # Ensure query_results is not None
            for worker, worker_tasks in query_results.items():
                for task_id, task_data in worker_tasks.items():
                    state, task_info = task_data
                    tasks.append({
                        "id": task_info["id"],
                        "name": task_info["name"],
                        "state": state,
                        "worker": worker,
                        "args": task_info.get("args", []),
                        "kwargs": task_info.get("kwargs", {}),
                        "type": task_info["type"],
                        "hostname": task_info["hostname"],
                        "time_start": task_info.get("time_start"),
                        "acknowledged": task_info.get("acknowledged"),
                        "delivery_info": task_info.get("delivery_info", {}),
                        "worker_pid": task_info.get("worker_pid"),
                    })

    return tasks


@celery_utils_router.get("/workers/stats", response_model=Dict[str, Dict])
async def get_workers_stats():
    """
    Returns statistics of all running workers.
    """
    i = celery_app.control.inspect()  # Use Inspect class
    stats = i.stats() if i else None  # Retrieve worker statistics

    if not stats:
        return {"error": "No workers are currently running or reachable."}

    return stats
