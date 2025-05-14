from fastapi import APIRouter, File ,UploadFile, HTTPException, File
import os
import json
import base64

celery_utils_router = APIRouter(prefix="/celery_utils", tags=["Celery utils Endpoints"])
