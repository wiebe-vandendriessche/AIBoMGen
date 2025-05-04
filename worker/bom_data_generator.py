import os
import json
import hashlib
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key

import base64


def generate_basic_bom_data(task_logger, environment, materials, products, fit_params=None, optional_params=None, link_file_minio_path=None, unique_dir=None):
    """
    Generate the basic BOM data as a dictionary, grouped into environment, materials, products, fit_params, and optional_params.

    Args:
        task_logger (Logger): Logger for logging task-specific information.
        environment (dict): Environment details for the training process.
        materials (dict): Input artifacts (e.g., model, dataset, dataset definition).
        products (dict): Output artifacts (e.g., trained model, metrics).
        fit_params (dict): Configuration details for the training process.
        optional_params (dict): Optional parameters for the model metadata.
        link_file_minio_path (str): MinIO path to the uploaded in-toto .link file.

    Returns:
        dict: The generated BOM data grouped by categories.
    """
    task_logger.info("Generating grouped BOM data...")

    # Grouped BOM data
    bom_data = {
        "environment": {
            "os": environment.get("os", "Unknown") or "Unknown",
            "python_version": environment.get("python_version", "Unknown") or "Unknown",
            "tensorflow_version": environment.get("tensorflow_version", "Unknown") or "Unknown",
            "cpu_count": environment.get("cpu_count", "Unknown") or "Unknown",
            "memory_total": environment.get("memory_total", "Unknown") or "Unknown",
            "disk_usage": environment.get("disk_usage", "Unknown") or "Unknown",
            "gpu_info": environment.get("gpu_info", []),
            "celery_task_info": {
                "task_id": environment.get("celery_task_info", {}).get("task_id", "Unknown") or "Unknown",
                "task_name": environment.get("celery_task_info", {}).get("task_name", "Unknown") or "Unknown",
                "queue": environment.get("celery_task_info", {}).get("queue", "Unknown") or "Unknown",
            },
            "docker_info": {
                "container_id": environment.get("docker_info", {}).get("container_id", "Unknown") or "Unknown",
                "image_name": environment.get("docker_info", {}).get("image_name", "Unknown") or "Unknown",
                "image_id": environment.get("docker_info", {}).get("image_id", "Unknown") or "Unknown",
            },
            "vulnerability_scan": environment.get("vulnerability_scan", {"error": "No vulnerability scan data available."}),
            "request_time": environment.get("request_time", "Unknown") or "Unknown",
            "start_training_time": environment.get("start_training_time", "Unknown") or "Unknown",
            "start_aibom_time": environment.get("start_aibom_time", "Unknown") or "Unknown",
            "training_time": environment.get("training_time", "Unknown") or "Unknown",
            "job_id": environment.get("job_id", "Unknown") or "Unknown",
            "unique_dir": environment.get("unique_dir", "Unknown") or "Unknown",
        },
        "materials": {
            path: {
                "sha256": details.get("sha256", "Unknown"),
                "local_path": details.get("local_path", "Unknown"),  # Use the passed local path directly
            }
            for path, details in materials.items()
        },
        "products": {
            path: {
                "sha256": details.get("sha256", "Unknown"),
                "local_path": details.get("local_path", "Unknown"),  # Use the passed local path directly
            }
            for path, details in products.items()
        },
        "fit_params": {
            key: value or "Unknown" for key, value in (fit_params or {}).items()
        },
        "optional_params": {
            "model_name": optional_params.get("model_name", "Unknown") or "Unknown",
            "model_version": optional_params.get("model_version", "Unknown") or "Unknown",
            "model_description": optional_params.get("model_description", "Unknown") or "Unknown",
            "author": optional_params.get("author", "Unknown") or "Unknown",
            "framework": optional_params.get("framework", "Unknown") or "Unknown",
            "license_name": optional_params.get("license_name", "Unknown") or "Unknown",
        },
    }

    # Add the .link file as an attestation
    if link_file_minio_path:
        bom_data["attestations"] = {
            "type": "in-toto",
            "minio_path": link_file_minio_path,
            "description": "in-toto .link file for artifact integrity verification",
        }
    else:
        bom_data["attestations"] = None  # No attestation if the .link file is missing

    task_logger.info("Grouped BOM data generated successfully.")
    return bom_data