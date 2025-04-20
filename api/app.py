from typing import Literal, Optional
from fastapi import FastAPI, Form, HTTPException, File, Query, UploadFile, Request  # Import Request
from fastapi.responses import FileResponse, RedirectResponse
from celery.result import AsyncResult
from celery import Celery
from dotenv import load_dotenv
import os
import shutil
import uuid
from shared.minio_utils import upload_file_to_minio, create_bucket_if_not_exists, list_files_in_bucket, generate_presigned_url
from shared.zip_utils import ZipValidationError, validate_zip_file
from contextlib import asynccontextmanager
import yaml
from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()

# Create a Celery instance in the FastAPI app to send tasks
celery_app = Celery(
    "aibomgen_worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the bucket exists when the API starts
    create_bucket_if_not_exists()
    yield

app = FastAPI(lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/submit_job_by_model_and_data")
@limiter.limit("5/minute")  # Limit to 5 requests per minute
async def submit_job(
    request: Request,
    # File uploads
    model: UploadFile = File(..., description="Model file to be trained (currently only .keras for tensorflow framework)."), 
    dataset: UploadFile = File(..., description="Dataset file for training (currently only csv and .zip for image data)."),
    dataset_definition: UploadFile = File(..., description="Dataset definition file (currently in YAML, see spec in project README)."),
    
    # Model metadata (moved to Form)
    framework: Literal["TensorFlow 2.16.1"] = Form(..., description="Currently, only TensorFlow 2.16.1 is supported."),
    model_name: Optional[str] = Form("", description="Name of the model."),
    model_version: Optional[str] = Form("", description="Version of the model."),
    model_description: Optional[str] = Form("", description="Description of the model."),
    author: Optional[str] = Form("", description="Author of the model."),
    model_type: Optional[str] = Form("", description="Type of the model (e.g., Image Classification)."),
    base_model: Optional[str] = Form("", description="Base model used (e.g., ResNet50)."),
    base_model_source: Optional[str] = Form("", description="Source URL of the base model."),
    intended_use: Optional[str] = Form("", description="Intended use of the model."),
    out_of_scope: Optional[str] = Form("", description="Out-of-scope use cases."),
    misuse_or_malicious: Optional[str] = Form("", description="Misuse or malicious use cases."),
    license_name: Optional[str] = Form("", description="License name for the model."),
    
    # Training parameters for model.fit (moved to Form)
    epochs: Optional[int] = Form(50, description="Number of epochs to train."),
    validation_split: Optional[float] = Form(0.2, description="Fraction of data to use for validation."),
    initial_epoch: Optional[int] = Form(0, description="Epoch at which to start training."),
    batch_size: Optional[int] = Form(32, description="Size of the batches of data. Default is 32."),
    steps_per_epoch: Optional[int] = Form(None, description="Total number of steps per epoch. If None or zero, it will be calculated with batch size."),
    validation_steps: Optional[int] = Form(None, description="Number of steps for validation. If None or zero, it will be calculated with batch size."),
    validation_freq: Optional[int] = Form(1, description="Specifies how many training epochs to run before a new validation run is performed. Default is 1 (every epoch)."),
):
    """
Submit a training job with model and dataset files, along with optional metadata and training parameters.

Args:
    
    Files Uploads:
        - model: The model file to be trained (currently only .keras for tensorflow framework).
        - dataset: The dataset file for training (currently only csv and .zip for image data). 
        - dataset_definition: The dataset definition file (currently in YAML, see spec in project README).
        
    Required Metadata:
        - framework: Framework used (currently only TensorFlow 2.16.1 is supported).
        
    Model Metadata:
        - model_name: Name of the model.
        - model_version: Version of the model.
        - model_description: Description of the model.
        - author: Author of the model.
        - model_type: Type of the model (e.g., Image Classification).
        - base_model: Base model used (e.g., ResNet50).
        - base_model_source: Source URL of the base model.
        - intended_use: Intended use of the model.
        - out_of_scope: Out-of-scope use cases.
        - misuse_or_malicious: Misuse or malicious use cases.
        - license_name: License name for the model.
        
    Training Parameters (optional):
        - epochs: Number of epochs to train.
        - validation_split: Fraction of data to use for validation.
        - initial_epoch: Epoch at which to start training.
        - batch_size: Size of the batches of data.
        - steps_per_epoch: Total number of steps per epoch.
        - validation_steps: Number of steps for validation.
        - validation_freq: Frequency of validation runs.
        
      
"""
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
        
        # Load the dataset definition to determine the dataset type
        with open(dataset_definition_path, "r") as f:
            dataset_definition_yaml = yaml.safe_load(f)
        
        dataset_type = dataset_definition_yaml.get("type", "csv")  # Default to 'csv' if not specified

        # Validate the dataset .zip file only if the type is 'image'
        if dataset_type == "image":
            try:
                validate_zip_file(dataset_path)  # Ensure the .zip file is safe
            except ZipValidationError as e:
                raise HTTPException(status_code=400, detail=str(e))

        # Upload files to MinIO
        model_url = upload_file_to_minio(model_path, f"{unique_dir}/model/{model.filename}")
        dataset_url = upload_file_to_minio(dataset_path, f"{unique_dir}/dataset/{dataset.filename}")
        dataset_definition_url = upload_file_to_minio(dataset_definition_path, f"{unique_dir}/definition/{dataset_definition.filename}")
        
        # Send Celery task with file URLs
        task = celery_app.send_task(
            'tasks.run_training',
            args=[
                unique_dir, model_url, dataset_url, dataset_definition_url,
                {
                    "model_name": model_name,
                    "model_version": model_version,
                    "model_description": model_description,
                    "author": author,
                    "framework": framework,
                    "model_type": model_type,
                    "base_model": base_model,
                    "base_model_source": base_model_source,
                    "intended_use": intended_use,
                    "out_of_scope": out_of_scope,
                    "misuse_or_malicious": misuse_or_malicious,
                    "license_name": license_name,
                },
                {
                    "epochs": epochs,
                    "validation_split": validation_split,
                    "initial_epoch": initial_epoch,
                    "batch_size": batch_size,
                    "steps_per_epoch": steps_per_epoch,
                    "validation_steps": validation_steps,
                    "validation_freq": validation_freq,
                }
            ]
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
async def download_artifact(job_id: str, artifact_name: str, redirect: bool = True, test_mode: bool = False):
    """
    Retrieve a presigned URL for downloading an artifact.
    """
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
        
        # Modify the presigned URL for testing purposes if test_mode is enabled
        if test_mode:
            presigned_url = presigned_url.replace("minio:9000", "localhost:9000")
        
        if redirect:
            # Redirect to the presigned URL for direct download
            return RedirectResponse(url=presigned_url)
        else:
            # Return the presigned URL in JSON format
            return {"artifact_name": artifact_name, "url": presigned_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")
