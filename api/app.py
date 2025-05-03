# === Standard Library Imports ===
import os
import shutil
import uuid
from contextlib import asynccontextmanager
import time
import io
import logging
import yaml

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
from in_toto.models.metadata import Metablock
from in_toto.verifylib import in_toto_verify
from in_toto.runlib import in_toto_match_products
from in_toto.exceptions import (
    SignatureVerificationError,
    LayoutExpiredError,
    LinkNotFoundError,
    ThresholdVerificationError,
    RuleVerificationError,
)

# === Local Imports ===
from shared.minio_utils import download_file_from_minio, upload_file_to_minio, list_files_in_bucket, TRAINING_BUCKET, create_bucket_if_not_exists, generate_presigned_url
from shared.zip_utils import ZipValidationError, validate_zip_file
from models import Job
import models
from database import SessionLocal, engine
from shared.in_toto_utils import record_artifact_as_dict

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

AUTH_ENABLED = os.getenv("AUTH_ENABLED", "true").lower() == "true"

if AUTH_ENABLED:
    azure_scheme = MultiTenantAzureAuthorizationCodeBearer(
        app_client_id=settings.APP_CLIENT_ID,
        scopes={
            f'api://{settings.APP_CLIENT_ID}/user_impersonation': 'user_impersonation',
        },
        validate_iss=False,
    )

    def get_current_user(user: User = Depends(azure_scheme)):
        return user
else:
    def get_current_user():
        class DummyUser:
            claims = {"oid": "anonymous"}
        return DummyUser()

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
    if AUTH_ENABLED:
        # Load OpenID config immediately if authentication is enabled
        await azure_scheme.openid_config.load_config()

    # Ensure the bucket exists when the API starts
    create_bucket_if_not_exists()
    
    # Call the retry mechanism during app startup
    initialize_database_with_retry()
    
    yield


# Create FastAPI app with lifespan and conditional Swagger UI oauth configuration
if AUTH_ENABLED:
    app = FastAPI(
        lifespan=lifespan,
        swagger_ui_oauth2_redirect_url='/oauth2-redirect',
        swagger_ui_init_oauth={
            'usePkceWithAuthorizationCodeGrant': True,
            'clientId': settings.OPENAPI_CLIENT_ID,
        },
    )
else:
    app = FastAPI(
        lifespan=lifespan,
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


@app.post("/submit_job_by_model_and_data", dependencies=[Depends(get_current_user)])
@limiter.limit("5/minute")  # Limit to 5 requests per minute
async def submit_job(
    request: Request,
    user: User = Depends(get_current_user),  # Use Depends to get the user object
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
        model_url = upload_file_to_minio(model_path, f"{unique_dir}/model/{model.filename}", TRAINING_BUCKET)
        dataset_url = upload_file_to_minio(dataset_path, f"{unique_dir}/dataset/{dataset.filename}", TRAINING_BUCKET)
        dataset_definition_url = upload_file_to_minio(dataset_definition_path, f"{unique_dir}/definition/{dataset_definition.filename}", TRAINING_BUCKET)

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
            ],
            queue='training_queue'
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

@app.get("/job_status/{job_id}", dependencies=[Depends(get_current_user)])
async def job_status(job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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

@app.get("/job_artifacts/{job_id}", dependencies=[Depends(get_current_user)])
async def get_job_artifacts(job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = user.claims.get("oid")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this job.")

    artifacts = list_files_in_bucket(f"{job.unique_dir}/", TRAINING_BUCKET)
    if not artifacts:
        raise HTTPException(status_code=404, detail="No artifacts found for this job.")
    return {"job_id": job_id, "artifacts": artifacts}

@app.get("/job_artifacts/{job_id}/{artifact_name}", dependencies=[Depends(get_current_user)])
async def download_artifact(job_id: str, artifact_name: str, user: User = Depends(get_current_user), db: Session = Depends(get_db), redirect: bool = True, test_mode: bool = False):
    user_id = user.claims.get("oid")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this job.")

    unique_dir = job.unique_dir
    all_files = list_files_in_bucket(f"{unique_dir}/", TRAINING_BUCKET)
    if not all_files:
        raise HTTPException(status_code=404, detail="No files found for this job.")

    matching_files = [file for file in all_files if file.endswith(f"/{artifact_name}")]
    if not matching_files:
        raise HTTPException(status_code=404, detail=f"Artifact '{artifact_name}' not found.")
    if len(matching_files) > 1:
        raise HTTPException(status_code=400, detail=f"Multiple artifacts named '{artifact_name}' found.")

    object_name = matching_files[0]
    presigned_url = generate_presigned_url(object_name, TRAINING_BUCKET, expiration=3600)  # URL valid for 1 hour

    if test_mode:
        presigned_url = presigned_url.replace("minio:9000", "localhost:9000")

    if redirect:
        return RedirectResponse(url=presigned_url)
    else:
        return {"artifact_name": artifact_name, "url": presigned_url}
    
    
@app.post("/verify_in-toto_link")
async def verify_in_toto(
    link_file: UploadFile = File(..., description="In-toto link file (e.g., run_training.<keyid>.link)"),
):
    try:
        # Define paths
        temp_dir = "/tmp/verify"
        os.makedirs(temp_dir, exist_ok=True)

        # Path to the signed layout file (now in /run/secrets)
        layout_path = "/run/secrets/signed_layout"

        # Check if the signed layout file exists
        if not os.path.exists(layout_path):
            raise HTTPException(
                status_code=500,
                detail="The signed layout file does not exist. Please ensure it is available at '/run/secrets/signed_layout'.",
            )

        # Save the uploaded link file temporarily
        link_path = os.path.join(temp_dir, link_file.filename)
        with open(link_path, "wb") as f:
            f.write(await link_file.read())

        # Debug: Log the link file path and directory contents
        print(f"Link file saved to: {link_path}")
        print(f"Files in {temp_dir}: {os.listdir(temp_dir)}")

        # Load the signed layout
        layout_metadata = Metablock.load(layout_path)

        # Verify the layout and link file
        in_toto_verify(
            metadata=layout_metadata,
            layout_key_dict=layout_metadata.signed.keys,
            link_dir_path=temp_dir,  # Directory containing the link file
        )

        # Detailed response
        response = {
            "status": "success",
            "message": "Verification successful.",
            "details": {
                "layout_signature": "Verified",
                "layout_expiration": "Valid",
                "link_signatures": "Verified",
                "threshold_verification": "Met",
                "artifact_rules": "All rules satisfied",
            },
        }

        return response

    except SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Verification failed: Invalid signature on the layout or link file.")
    except LayoutExpiredError:
        raise HTTPException(status_code=400, detail="Verification failed: The layout has expired.")
    except LinkNotFoundError:
        raise HTTPException(status_code=400, detail="Verification failed: No valid link files found for the step.")
    except ThresholdVerificationError:
        raise HTTPException(status_code=400, detail="Verification failed: Threshold requirements not met for the step.")
    except RuleVerificationError as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: Artifact rule violation. {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")
    
@app.post("/verify_file_hash")
async def verify_file_hash(
    link_file: UploadFile = File(..., description="In-toto link file (e.g., run_training.<keyid>.link)"),
    uploaded_file: UploadFile = File(..., description="File to verify (e.g., a model or metrics file)."),
):
    """
    Verify the hash of an uploaded file against the in-toto link file metadata.
    """
    try:
        # Define paths
        temp_dir = "/tmp/verify"
        os.makedirs(temp_dir, exist_ok=True)

        # Save the uploaded link file temporarily
        link_path = os.path.join(temp_dir, link_file.filename)
        with open(link_path, "wb") as f:
            f.write(await link_file.read())

        # Save the uploaded file to verify temporarily
        file_to_verify_path = os.path.join(temp_dir, uploaded_file.filename)
        with open(file_to_verify_path, "wb") as f:
            f.write(await uploaded_file.read())

        # Load the link file
        link_metadata = Metablock.load(link_path)

        # Compute the hash of the uploaded file
        computed_hash = record_artifact_as_dict(file_to_verify_path)

        # Check if the hash matches any material or product in the link file
        recorded_hash = None
        for path, hash_dict in {**link_metadata.signed.materials, **link_metadata.signed.products}.items():
            if os.path.basename(path) == uploaded_file.filename:
                recorded_hash = hash_dict
                break

        if not recorded_hash:
            raise HTTPException(
                status_code=404,
                detail=f"File '{uploaded_file.filename}' not found in materials or products of the link file.",
            )

        # Compare the hashes
        if computed_hash != recorded_hash:
            return {
                "status": "failure",
                "message": "Hash mismatch.",
                "details": {
                    "file_name": uploaded_file.filename,
                    "computed_hash": computed_hash,
                    "recorded_hash": recorded_hash,
                },
            }

        return {
            "status": "success",
            "message": "Hash matches the recorded metadata.",
            "details": {
                "file_name": uploaded_file.filename,
                "hash": computed_hash,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")
    
    
@app.post("/verify_minio_artifacts")
async def verify_minio_artifacts(
    link_file: UploadFile = File(..., description="In-toto link file (e.g., run_training.<keyid>.link)"),
):
    """
    Verify materials and products stored in MinIO against the in-toto link file metadata.
    If this has mismatches, this means that the artifacts in MinIO are not the same as those recorded in the link file.
    This could be due to a malicious actor that has access to MinIO tampering with the files.
    Because the link file is signed, the malicious actor cannot change the link file itself to match the tampered files.
    """
    try:
        # Define paths
        temp_dir = "/tmp/verify"
        os.makedirs(temp_dir, exist_ok=True)

        # Save the uploaded link file temporarily
        link_path = os.path.join(temp_dir, link_file.filename)
        with open(link_path, "wb") as f:
            f.write(await link_file.read())

        # Load the link file
        link_metadata = Metablock.load(link_path)

        # Prepare to store verification results
        mismatched_materials = []
        mismatched_products = []
        verified_materials = []
        verified_products = []

        # Extract unique_dir dynamically from the first material or product path
        all_paths = list(link_metadata.signed.materials.keys()) + list(link_metadata.signed.products.keys())
        if not all_paths:
            raise HTTPException(status_code=400, detail="No materials or products found in the link file.")
        
        # Assume the unique_dir is the first part of the path (e.g., "2809d3f5-72d8-4097-932c-401f3433c255")
        unique_dir = all_paths[0].split("/")[0]

        # Verify materials
        for material_path, recorded_hash in link_metadata.signed.materials.items():
            minio_path = material_path  # Full path already includes unique_dir
            local_path = os.path.join(temp_dir, os.path.basename(material_path))

            # Download material from MinIO
            try:
                download_file_from_minio(minio_path, local_path, TRAINING_BUCKET)
            except Exception as e:
                mismatched_materials.append({
                    "path": material_path,
                    "error": f"Failed to download from MinIO: {str(e)}"
                })
                continue

            # Compute hash and compare
            computed_hash = record_artifact_as_dict(local_path)
            if computed_hash != recorded_hash:
                mismatched_materials.append({
                    "path": material_path,
                    "computed_hash": computed_hash,
                    "recorded_hash": recorded_hash,
                })
            else:
                verified_materials.append(material_path)

        # Verify products
        for product_path, recorded_hash in link_metadata.signed.products.items():
            minio_path = product_path  # Full path already includes unique_dir
            local_path = os.path.join(temp_dir, os.path.basename(product_path))

            # Download product from MinIO
            try:
                download_file_from_minio(minio_path, local_path, TRAINING_BUCKET)
            except Exception as e:
                mismatched_products.append({
                    "path": product_path,
                    "error": f"Failed to download from MinIO: {str(e)}"
                })
                continue

            # Compute hash and compare
            computed_hash = record_artifact_as_dict(local_path)
            if computed_hash != recorded_hash:
                mismatched_products.append({
                    "path": product_path,
                    "computed_hash": computed_hash,
                    "recorded_hash": recorded_hash,
                })
            else:
                verified_products.append(product_path)

        # Prepare response
        response = {
            "status": "success" if not mismatched_materials and not mismatched_products else "failure",
            "verified_materials": verified_materials,
            "verified_products": verified_products,
            "mismatched_materials": mismatched_materials,
            "mismatched_products": mismatched_products,
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")
    
    