from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from celery.result import AsyncResult
from celery import Celery
from dotenv import load_dotenv
import os
import shutil
import uuid

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
async def submit_job(
    model: UploadFile = File(...), 
    dataset: UploadFile = File(...),
    dataset_definition: UploadFile = File(...)
):
    try:
        # Create a unique directory for this upload
        unique_dir = os.path.join(UPLOAD_DIR, str(uuid.uuid4()))
        os.makedirs(unique_dir, exist_ok=True)

        # Save model file
        model_path = os.path.join(unique_dir, model.filename)
        with open(model_path, "wb") as buffer:
            shutil.copyfileobj(model.file, buffer)
        os.sync()  # Ensures file is written to disk

        # Save dataset file
        dataset_path = os.path.join(unique_dir, dataset.filename)
        with open(dataset_path, "wb") as buffer:
            shutil.copyfileobj(dataset.file, buffer)
        os.sync()  # Ensures file is written to disk
        
        # Save dataset definition file
        dataset_definition_path = os.path.join(unique_dir, dataset_definition.filename)
        with open(dataset_definition_path, "wb") as buffer:
            shutil.copyfileobj(dataset_definition.file, buffer)

        # Verify files exist before proceeding
        if not os.path.exists(model_path):
            raise HTTPException(status_code=500, detail=f"Model file {model.filename} was not properly saved.")
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=500, detail=f"Dataset file {dataset.filename} was not properly saved.")
        if not os.path.exists(dataset_definition_path):
            raise HTTPException(status_code=500, detail=f"Dataset definition file {dataset_definition.filename} was not properly saved.")

        # Send Celery task with the unique directory
        task = celery_app.send_task(
            'tasks.run_training',
            args=[model.filename, dataset.filename, dataset_definition.filename, unique_dir]
        )
        return {"job_id": task.id, "unique_dir": unique_dir, "status": "Training started", "model_path": model_path, "dataset_path": dataset_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task submission failed: {str(e)}")

@app.get("/job_status/{job_id}")
async def job_status(job_id: str):
    job = AsyncResult(job_id, app=celery_app)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {"status": job.status, "result": job.result}


# This helper function retrieves the unique directory for the job ID
def get_unique_dir_from_job(job_id: str):
    job = AsyncResult(job_id, app=celery_app)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    directory = job.result.get("unique_dir")
    if not directory:
        raise HTTPException(status_code=404, detail="Unique directory not found.")
    return os.path.join(UPLOAD_DIR, directory)

@app.get("/job_artifacts/{job_id}")
async def get_job_artifacts(job_id: str):
    unique_dir = get_unique_dir_from_job(job_id)
    if not os.path.exists(unique_dir):
        raise HTTPException(status_code=404, detail="Job artifacts not found.")

    # List available artifacts
    artifacts = os.listdir(unique_dir)
    return {"job_id": job_id, "artifacts": artifacts}

@app.get("/job_artifacts/{job_id}/{artifact_name}")
async def download_artifact(job_id: str, artifact_name: str):
    unique_dir = get_unique_dir_from_job(job_id)
    if not os.path.exists(unique_dir):
        raise HTTPException(status_code=404, detail="Job artifacts not found.")
    artifact_path = os.path.join(UPLOAD_DIR, unique_dir, artifact_name)
    if not os.path.exists(artifact_path):
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return FileResponse(artifact_path, media_type="application/octet-stream", filename=artifact_name)
