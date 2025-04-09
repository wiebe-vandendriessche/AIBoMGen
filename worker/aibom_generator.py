import os
import json
import hashlib
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

def generate_hash(file_path):
    """Generate a SHA-256 hash for a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_basic_aibom(input_files, output_files, config, environment):
    """Generate the basic AIBoM as a dictionary."""
    aibom = {
        "environment": environment,
        "inputs": {file: generate_hash(file) for file in input_files},
        "outputs": {file: generate_hash(file) for file in output_files},
        "config": config,
        "environment": environment,
    }
    return aibom

def sign_aibom(aibom, private_key_path):
    """Sign the AIBoM using the platform's private key."""
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None)
    
    aibom_json = json.dumps(aibom, indent=4).encode()
    signature = private_key.sign(
        aibom_json,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return signature

def save_aibom(aibom, signature, unique_dir):
    """Save the AIBoM and its signature to files."""
    aibom_path = os.path.join(unique_dir, "aibom.json")
    signature_path = os.path.join(unique_dir, "aibom.sig")
    
    with open(aibom_path, "w") as f:
        json.dump(aibom, f, indent=4)
    
    with open(signature_path, "wb") as f:
        f.write(signature)