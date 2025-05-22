# === Standard Library Imports ===
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Annotated
import models
# === Third-Party Library Imports ===
from celery import Celery
from celery_utils_endpoints import celery_utils_router
from database import SessionLocal, engine
from developer_endpoints import developer_router
from fastapi import (Depends, FastAPI)
from fastapi.middleware.cors import CORSMiddleware
from fastapi_azure_auth import MultiTenantAzureAuthorizationCodeBearer
from fastapi_azure_auth.user import User
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from shared.minio_utils import create_bucket_if_not_exists
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from verifier_endpoints import verifier_router
from auth_utils import AUTH_ENABLED

# === Load Environment Variables ===
logger = logging.getLogger(__name__)

# === Azure Auth Settings Configuration ===


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = [
        "http://localhost:8000", "http://localhost:3000"]
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()


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
        from auth_utils import azure_scheme
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
            # Create tables if they don't exist
            models.Base.metadata.create_all(bind=engine)
            logger.info("Database initialized successfully.")
            return
        except OperationalError as e:
            logger.warning(
                f"Attempt {attempt}/{retries}: Database connection failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    logger.error("Failed to connect to the database after multiple attempts.")
    raise RuntimeError("Database initialization failed.")


# === Middleware Setup ===
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.BACKEND_CORS_ORIGINS],
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


# === Routers ===
# === Include Routers in the Main App ===
app.include_router(developer_router)
app.include_router(verifier_router)
app.include_router(celery_utils_router)
