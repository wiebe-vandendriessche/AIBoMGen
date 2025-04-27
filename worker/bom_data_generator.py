import os
import json
import hashlib
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key

import base64

def generate_hash(file_path):
    """Generate a SHA-256 hash for a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_basic_bom_data(input_files, output_files, fit_params, environment, optional_params=None):
    """
    Generate the basic BOM data as a dictionary.
    Args:
        input_files (list): List of input file paths.
        output_files (list): List of output file paths.
        fit_params (dict): Configuration details for the training process.
        environment (dict): Environment details for the training process.
        optional_params (dict): Optional parameters for the model metadata.
    Returns:
        dict: The generated BOM data.
    """
        
    # Extract paths from input_files
    dataset_path = input_files.get("dataset_path")
    model_path = input_files.get("model_path")
    dataset_definition_path = input_files.get("dataset_definition_path")

    # Extract paths from output_files
    output_model_path = output_files.get("output_model_path")
    metrics_path = output_files.get("metrics_path")
    logs_path = output_files.get("logs_path")

    # Example static values for the model (these can be dynamically set later if needed)
    model_name = optional_params.get("model_name", "Unknown")
    model_version = optional_params.get("model_version", "Unknown")
    model_description = optional_params.get("model_description", "Unknown")
    author = optional_params.get("author", "Unknown")
    framework = optional_params.get("framework", "Unknown")
    model_type = optional_params.get("model_type", "Unknown")
    base_model = optional_params.get("base_model", "Unknown")
    base_model_source = optional_params.get("base_model_source", "Unknown")
    intended_use = optional_params.get("intended_use", "Unknown")
    out_of_scope = optional_params.get("out_of_scope", "Unknown")
    misuse_or_malicious = optional_params.get("misuse_or_malicious", "Unknown")
    license_name = optional_params.get("license_name", "Unknown")
    
    # Generate dataset information
    datasets = {}
    if dataset_path and dataset_definition_path:
        datasets["training_data"] = {
            "version": "Unknown",
            "source": dataset_path,
            "license": "Unknown",  # Replace with actual license if available
            "description": "Training dataset for the model",
            "definition": dataset_definition_path,  # Include dataset definition path
        }
        
    # Generate input artifacts
    input_artifacts = {}
    if model_path:
        input_artifacts["input_model"] = {
            "path": model_path,
            "hash": generate_hash(model_path),
            "description": "Input model file used for training",
        }
    if dataset_path:
        input_artifacts["training_dataset"] = {
            "path": dataset_path,
            "hash": generate_hash(dataset_path),
            "description": "Dataset used for training",
        }
    
    # Generate output artifacts
    output_artifacts = {}
    if output_model_path:
        output_artifacts["trained_model"] = {
            "path": output_model_path,
            "hash": generate_hash(output_model_path),
            "description": "Trained model file",
        }
    if metrics_path:
        output_artifacts["metrics"] = {
            "path": metrics_path,
            "hash": generate_hash(metrics_path),
            "description": "Metrics generated during training",
        }
    if logs_path:
        output_artifacts["logs"] = {
            "path": logs_path,
            "hash": generate_hash(logs_path),
            "description": "Logs generated during training",
        }
    
    # Construct the BOM data
    bom_data = {
        "model_name": model_name,
        "model_version": model_version,
        "model_description": model_description,
        "framework": framework,
        "model_type": model_type,
        "base_model": base_model,
        "base_model_source": base_model_source,
        "author": author,
        "intended_use": intended_use,
        "out_of_scope": out_of_scope,
        "misuse_or_malicious": misuse_or_malicious,
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
        "datasets": datasets,
        "input_artifacts": input_artifacts,
        "output_artifacts": output_artifacts,
    }

    return bom_data

def sign_basic_bom_data(bom_data, private_key_path):
    """
    Sign the BOM data using an RSA private key.

    Args:
        bom_data (dict): The BOM data to sign.
        private_key_path (str): Path to the private key file.

    Returns:
        bytes: The signature of the BOM data.
    """
    # Serialize the BOM data to JSON
    bom_data_json = json.dumps(bom_data, indent=4).encode("utf-8")

    # Load the RSA private key
    with open(private_key_path, "rb") as key_file:
        private_key = load_pem_private_key(key_file.read(), password=None)

    # Sign the BOM data using RSA with PKCS1v15 padding and SHA256 hash
    signature = private_key.sign(
        bom_data_json,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature