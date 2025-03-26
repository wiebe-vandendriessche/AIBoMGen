from fastapi import FastAPI, HTTPException, File, UploadFile
from celery.result import AsyncResult
from celery import Celery
from dotenv import load_dotenv
import os
import shutil

load_dotenv()

# Create a Celery instance in the FastAPI app to send tasks
celery_app = Celery(
    "aibomgen_worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

app = FastAPI()

# Shared directory for file exchange between FastAPI and Celery
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/submit_job_by_model_and_data")
async def submit_job(model: UploadFile = File(...), dataset: UploadFile = File(...)):
    try:
        # Save model file
        model_path = os.path.join(UPLOAD_DIR, model.filename)
        with open(model_path, "wb") as buffer:
            shutil.copyfileobj(model.file, buffer)
        os.sync()  # Ensures file is written to disk

        # Save dataset file
        dataset_path = os.path.join(UPLOAD_DIR, dataset.filename)
        with open(dataset_path, "wb") as buffer:
            shutil.copyfileobj(dataset.file, buffer)
        os.sync()  # Ensures file is written to disk

        # Verify file exists before proceeding
        if not os.path.exists(model_path):
            raise HTTPException(status_code=500, detail=f"Model file {model.filename} was not properly saved.")
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=500, detail=f"Dataset file {dataset.filename} was not properly saved.")

        # Send Celery task after ensuring files exist
        task = celery_app.send_task(
            'tasks.run_training',
            args=[model.filename, dataset.filename]  # Send filenames to worker
        )
        return {"job_id": task.id, "status": "Training started", "model_path": model_path, "dataset_path": dataset_path}

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
