from fastapi import FastAPI, HTTPException, File, UploadFile
from celery.result import AsyncResult
from celery import Celery
from dotenv import load_dotenv
import os

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

@app.post("/submit_job_by_model_file")
async def submit_job(file: UploadFile = File(...)):
    try:
        # Save the uploaded file in the shared volume
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Send Celery task with the file path
        task = celery_app.send_task(
            'tasks.run_training',
            args=[file.filename]  # Send filename instead of just triggering the task
        )
        return {"job_id": task.id, "status": "Training started", "file_path": file_path}
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
