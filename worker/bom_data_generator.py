import os
import json
import hashlib
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key

import base64


def generate_basic_bom_data(task_logger, environment, materials, products, fit_params=None, optional_params=None, link_file_minio_path=None):
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
            "os": environment.get("os", "Unknown"),
            "python_version": environment.get("python_version", "Unknown"),
            "tensorflow_version": environment.get("tensorflow_version", "Unknown"),
            "cpu_count": environment.get("cpu_count", "Unknown"),
            "memory_total": environment.get("memory_total", "Unknown"),
            "disk_usage": environment.get("disk_usage", "Unknown"),
            "gpu_info": environment.get("gpu_info", []),
            "celery_task_info": environment.get("celery_task_info", {}),
            "docker_info": environment.get("docker_info", {}),
            "vulnerability_scan": environment.get("vulnerability_scan", {}),
            "request_time": environment.get("request_time", "Unknown"),
            "start_training_time": environment.get("start_training_time", "Unknown"),
            "start_aibom_time": environment.get("start_aibom_time", "Unknown"),
            "training_time": environment.get("training_time", "Unknown"),
            "job_id": environment.get("job_id", "Unknown"),
            "unique_dir": environment.get("unique_dir", "Unknown"),
        },
        "materials": {
            path: {
                "sha256": details.get("sha256", "Unknown")
            }
            for path, details in materials.items()
        },
        "products": {
            path: {
                "sha256": details.get("sha256", "Unknown")
            }
            for path, details in products.items()
        },
        "fit_params": fit_params or {},
        "optional_params": {
            "model_name": optional_params.get("model_name", "Unknown"),
            "model_version": optional_params.get("model_version", "Unknown"),
            "model_description": optional_params.get("model_description", "Unknown"),
            "author": optional_params.get("author", "Unknown"),
            "framework": optional_params.get("framework", "Unknown"),
            "license_name": optional_params.get("license_name", "Unknown"),
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