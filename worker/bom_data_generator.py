import os
import json
import hashlib
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key

import base64


def generate_basic_bom_data(fit_params, environment, optional_params=None, link_file_minio_path=None):
    """
    Generate the basic BOM data as a dictionary, including the .link file as an attestation
    and some duplicate components (e.g., datasets) for visibility.

    Args:
        fit_params (dict): Configuration details for the training process.
        environment (dict): Environment details for the training process.
        optional_params (dict): Optional parameters for the model metadata.
        link_file_path (str): Path to the in-toto .link file.

    Returns:
        dict: The generated BOM data.
    """
    # Example static values for the model (these can be dynamically set later if needed)
    model_name = optional_params.get("model_name", "Unknown")
    model_version = optional_params.get("model_version", "Unknown")
    model_description = optional_params.get("model_description", "Unknown")
    author = optional_params.get("author", "Unknown")
    framework = optional_params.get("framework", "Unknown")
    license_name = optional_params.get("license_name", "Unknown")

    # Construct the BOM data
    bom_data = {
        "model_name": model_name,
        "model_version": model_version,
        "model_description": model_description,
        "framework": framework,
        "author": author,
        "license": license_name,
        "training_environment": {
            "os": environment.get("os", "Unknown"),
            "python_version": environment.get("python_version", "3.9"),
            "tensorflow_version": environment.get("tensorflow_version", "Unknown"),
            "request_time": environment.get("request_time", "Unknown"),
            "start_training_time": environment.get("start_training_time", "Unknown"),
            "start_aibom_time": environment.get("start_aibom_time", "Unknown"),
            "training_time": environment.get("training_time", "Unknown"),
            "job_id": environment.get("job_id", "Unknown"),
            "unique_dir": environment.get("unique_dir", "Unknown"),
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

    return bom_data