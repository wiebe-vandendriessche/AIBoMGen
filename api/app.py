import hashlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from celery import Celery
from datasets import load_dataset
from typing import Optional


# Create a Celery instance in the FastAPI app to send tasks
celery_app = Celery(
    "aibomgen_worker",
    broker="redis://redis:6379/0",  # Redis broker
    backend="redis://redis:6379/0",  # Redis backend
)

app = FastAPI()

class JobParams(BaseModel):
    model_name: str
    dataset_name: str  # Name of the Hugging Face dataset

    # Optional training parameters
    num_train_epochs: Optional[int] = 1             # Just 1 epoch for fast testing
    per_device_train_batch_size: Optional[int] = 4  # Small batch size for fast testing
    per_device_eval_batch_size: Optional[int] = 4   # Small batch size for fast testing
    learning_rate: Optional[float] = 5e-5           # Default learning rate
    logging_steps: Optional[int] = 32              # Log more frequently for faster monitoring
    save_steps: Optional[int] = 500                 # Save frequently during testing
    eval_steps: Optional[int] = 500                 # Evaluation steps for fast monitoring
    warmup_steps: Optional[int] = 0                 # Very few warmup steps for faster start
    weight_decay: Optional[float] = 0.0             # Default weight decay
    max_grad_norm: Optional[float] = 1.0            # Keep this default for gradient clipping
    evaluation_strategy: Optional[str] = "epoch"    # Evaluate frequently during training
    logging_strategy: Optional[str] = "steps"

@app.post("/submit_job")
async def submit_job(job_params: JobParams):
    """Submit training job with Hugging Face dataset."""
    try:
        dataset = load_dataset(job_params.dataset_name)

        dataset_hash = compute_dataset_hash(dataset)

        task = celery_app.send_task(
            'tasks.run_training',
            args=[job_params.model_dump(), dataset_hash]
        )
        return {"job_id": task.id, "status": "Training started", "dataset_hash": dataset_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task submission failed: {str(e)}")

@app.get("/job_status/{job_id}")
async def job_status(job_id: str):
    job = AsyncResult(job_id, app=celery_app)
    return {"status": job.status, "result": job.result}

@app.get("/job_result/{job_id}")
async def job_result(job_id: str):
    job = AsyncResult(job_id, app=celery_app)
    if job.status == 'SUCCESS':
        return {"result": job.result}
    else:
        return {"status": job.status}


def compute_dataset_hash(dataset):
    """Compute a hash of the dataset (e.g., based on its content)."""
    sha256 = hashlib.sha256()
    for example in dataset:
        sha256.update(str(example).encode("utf-8"))
    return sha256.hexdigest()
