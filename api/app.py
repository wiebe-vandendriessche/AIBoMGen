# === Standard Library Imports ===
import os
import shutil
import uuid
from contextlib import asynccontextmanager
import time

# === Third-Party Library Imports ===
from celery import Celery
from celery.result import AsyncResult
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    Security,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi_azure_auth import MultiTenantAzureAuthorizationCodeBearer
from fastapi_azure_auth.user import User
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from typing import Annotated, Literal, Optional
import logging
import yaml

# === Local Imports ===
from shared.minio_utils import (
    upload_file_to_minio,
    create_bucket_if_not_exists,
    list_files_in_bucket,
    generate_presigned_url,
)
from shared.zip_utils import ZipValidationError, validate_zip_file
from models import Job
import models
from database import SessionLocal, engine


# === Load Environment Variables ===
logger = logging.getLogger(__name__)

# === Azure Auth Settings Configuration ===
class Settings(BaseSettings):
    BACKEND_CORS_ORIGINGS: list[str | AnyHttpUrl] = ["http://localhost:8000"]
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()
    
# === Celery Configuration ===
celery_app = Celery(
    "aibomgen_worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

# === Authentication Setup ===
azure_scheme = MultiTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.APP_CLIENT_ID,
    scopes={
        f'api://{settings.APP_CLIENT_ID}/user_impersonation': 'user_impersonation',
    },
    validate_iss=False,
)

# === Database Initialization ===
def get_db():
    """
    Dependency to provide a synchronous database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)] 

# === FastAPI Application Setup ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load OpenID config immediately
    await azure_scheme.openid_config.load_config()

    # Ensure the bucket exists when the API starts
    create_bucket_if_not_exists()
    
    # Call the retry mechanism during app startup
    initialize_database_with_retry()
    
    yield


# Create FastAPI app with lifespan and Swagger UI oauth configuration
app = FastAPI(
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': settings.OPENAPI_CLIENT_ID,
    },
)

# === Database Initialization with Retry ===
def initialize_database_with_retry(retries=60, delay=10):
    """
    Retry mechanism to wait for the database to become available.
    """
    for attempt in range(1, retries + 1):
        try:
            models.Base.metadata.create_all(bind=engine)  # Create tables if they don't exist
            logger.info("Database initialized successfully.")
            return
        except OperationalError as e:
            logger.warning(f"Attempt {attempt}/{retries}: Database connection failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    logger.error("Failed to connect to the database after multiple attempts.")
    raise RuntimeError("Database initialization failed.")



# === Middleware Setup ===
if settings.BACKEND_CORS_ORIGINGS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINGS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )



# === Rate Limiting Setup from SlowAPI ===
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# === Database session dependency === #

def get_db():
    """
    Dependency to provide a synchronous database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/submit_job_by_model_and_data", dependencies=[Security(azure_scheme)])
@limiter.limit("5/minute")  # Limit to 5 requests per minute
async def submit_job(
    request: Request,
    user: User = Depends(azure_scheme),  # Use Depends to get the user object
    db: Session = Depends(get_db),  # Inject the database session
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
    # Save the user ID from the Azure token
    user_id = user.claims.get("oid")  # Get the user's Azure Object ID
    
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
        
        # Store job metadata in the database
        job = Job(
            id=task.id,
            user_id=user_id,
            unique_dir=unique_dir,
        )
        db.add(job)
        db.commit()
        
        return {"job_id": task.id, "status": "Training started", "unique_dir": unique_dir}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task submission failed: {str(e)}")

@app.get("/job_status/{job_id}", dependencies=[Security(azure_scheme)])
async def job_status(job_id: str, user: User = Depends(azure_scheme), db: Session = Depends(get_db)):
    user_id = user.claims.get("oid")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this job.")

    celery_task = AsyncResult(job_id, app=celery_app)
    if not celery_task:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {"status": celery_task.status, "result": celery_task.result}

@app.get("/job_artifacts/{job_id}", dependencies=[Security(azure_scheme)])
async def get_job_artifacts(job_id: str, user: User = Depends(azure_scheme), db: Session = Depends(get_db)):
    user_id = user.claims.get("oid")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this job.")

    artifacts = list_files_in_bucket(f"{job.unique_dir}/")
    if not artifacts:
        raise HTTPException(status_code=404, detail="No artifacts found for this job.")
    return {"job_id": job_id, "artifacts": artifacts}

@app.get("/job_artifacts/{job_id}/{artifact_name}", dependencies=[Security(azure_scheme)])
async def download_artifact(job_id: str, artifact_name: str, user: User = Depends(azure_scheme), db: Session = Depends(get_db), redirect: bool = True, test_mode: bool = False):
    user_id = user.claims.get("oid")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this job.")

    unique_dir = job.unique_dir
    all_files = list_files_in_bucket(f"{unique_dir}/")
    if not all_files:
        raise HTTPException(status_code=404, detail="No files found for this job.")

    matching_files = [file for file in all_files if file.endswith(f"/{artifact_name}")]
    if not matching_files:
        raise HTTPException(status_code=404, detail=f"Artifact '{artifact_name}' not found.")
    if len(matching_files) > 1:
        raise HTTPException(status_code=400, detail=f"Multiple artifacts named '{artifact_name}' found.")

    object_name = matching_files[0]
    presigned_url = generate_presigned_url(object_name)

    if test_mode:
        presigned_url = presigned_url.replace("minio:9000", "localhost:9000")

    if redirect:
        return RedirectResponse(url=presigned_url)
    else:
        return {"artifact_name": artifact_name, "url": presigned_url}
