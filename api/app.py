from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from celery.result import AsyncResult
from celery import Celery
from dotenv import load_dotenv
import os
import shutil
import uuid
from shared.minio_utils import upload_file_to_minio, create_bucket_if_not_exists, list_files_in_bucket, generate_presigned_url

load_dotenv()

# Create a Celery instance in the FastAPI app to send tasks
celery_app = Celery(
    "aibomgen_worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Ensure the bucket exists when the API starts
    create_bucket_if_not_exists()

@app.post("/submit_job_by_model_and_data")
async def submit_job(
    model: UploadFile = File(...), 
    dataset: UploadFile = File(...),
    dataset_definition: UploadFile = File(...)
):
    try:
        # Generate a unique directory for the job
        unique_dir = str(uuid.uuid4())
        
        # Save files temporarily
        temp_dir = os.path.join("/tmp", unique_dir)
        os.makedirs(temp_dir, exist_ok=True)

        model_path = os.path.join(temp_dir, model.filename)
        dataset_path = os.path.join(temp_dir, dataset.filename)
        dataset_definition_path = os.path.join(temp_dir, dataset_definition.filename)

        with open(model_path, "wb") as buffer:
            shutil.copyfileobj(model.file, buffer)
        with open(dataset_path, "wb") as buffer:
            shutil.copyfileobj(dataset.file, buffer)
        with open(dataset_definition_path, "wb") as buffer:
            shutil.copyfileobj(dataset_definition.file, buffer)

        # Upload files to MinIO
        model_url = upload_file_to_minio(model_path, f"{unique_dir}/model/{model.filename}")
        dataset_url = upload_file_to_minio(dataset_path, f"{unique_dir}/dataset/{dataset.filename}")
        dataset_definition_url = upload_file_to_minio(dataset_definition_path, f"{unique_dir}/definition/{dataset_definition.filename}")

        # Send Celery task with file URLs
        task = celery_app.send_task(
            'tasks.run_training',
            args=[unique_dir, model_url, dataset_url, dataset_definition_url]
        )
        return {"job_id": task.id, "status": "Training started", "unique_dir": unique_dir}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task submission failed: {str(e)}")

@app.get("/job_status/{job_id}")
async def job_status(job_id: str):
    job = AsyncResult(job_id, app=celery_app)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {"status": job.status, "result": job.result}

@app.get("/job_artifacts/{job_id}")
async def get_job_artifacts(job_id: str):
    try:
        # Retrieve the unique directory from the Celery task result
        job = AsyncResult(job_id, app=celery_app)
        if not job or not job.result:
            raise HTTPException(status_code=404, detail="Job not found or not completed.")
        unique_dir = job.result.get("unique_dir")
        if not unique_dir:
            raise HTTPException(status_code=404, detail="Unique directory not found.")

        # List all files in the job-specific directory in MinIO
        artifacts = list_files_in_bucket(f"{unique_dir}/")
        if not artifacts:
            raise HTTPException(status_code=404, detail="No artifacts found for this job.")
        return {"job_id": job_id, "artifacts": artifacts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve artifacts: {str(e)}")


@app.get("/job_artifacts/{job_id}/{artifact_name}")
async def download_artifact(job_id: str, artifact_name: str):
    try:
        # Retrieve the unique directory from the Celery task result
        job = AsyncResult(job_id, app=celery_app)
        if not job or not job.result:
            raise HTTPException(status_code=404, detail="Job not found or not completed.")
        unique_dir = job.result.get("unique_dir")
        if not unique_dir:
            raise HTTPException(status_code=404, detail="Unique directory not found.")

        # List all files in the unique directory
        all_files = list_files_in_bucket(f"{unique_dir}/")
        if not all_files:
            raise HTTPException(status_code=404, detail="No files found for this job.")

        # Search for the artifact in the directory structure
        matching_files = [file for file in all_files if file.endswith(f"/{artifact_name}")]
        if not matching_files:
            raise HTTPException(status_code=404, detail=f"Artifact '{artifact_name}' not found.")
        if len(matching_files) > 1:
            raise HTTPException(status_code=400, detail=f"Multiple artifacts named '{artifact_name}' found.")

        # Generate a presigned URL for the matching artifact
        object_name = matching_files[0]
        presigned_url = generate_presigned_url(object_name)
        return {"artifact_name": artifact_name, "url": presigned_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")
