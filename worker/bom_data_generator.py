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
    Generate the basic BOM data as a dictionary, including the .link file as an attestation
    and some duplicate components (e.g., datasets) for visibility.

    Args:
        task_logger (Logger): Logger for logging task-specific information.
        environment (dict): Environment details for the training process.
        materials (dict): Input artifacts (e.g., model, dataset, dataset definition).
        products (dict): Output artifacts (e.g., trained model, metrics).
        fit_params (dict): Configuration details for the training process.
        optional_params (dict): Optional parameters for the model metadata.
        link_file_minio_path (str): MinIO path to the uploaded in-toto .link file.

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

    serialized_environment = json.dumps(environment, indent=4)

    # Construct the BOM data
    bom_data = {
        "model_name": model_name,
        "model_version": model_version,
        "model_description": model_description,
        "framework": framework,
        "author": author,
        "license": license_name,
        "training_environment": serialized_environment,
        "training_parameters": fit_params,
        "materials": {
            name: {
                "path": path,
                "hash": materials[path]["sha256"],
            }
            for name, path in materials.items()
        },
        "products": {
            name: {
                "path": path,
                "hash": products[path]["sha256"],
            }
            for name, path in products.items()
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

    task_logger.info("BOM data generated successfully.")
    return bom_data