from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

def generate_private_key(file_path="private_key.pem"):
    """Generate an RSA private key and save it as a PEM file."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(file_path, "wb") as f:
        f.write(pem)
    print(f"Private key saved to {file_path}")


worker_dir = "./secrets"
os.makedirs(worker_dir, exist_ok=True)  # Ensure the worker directory exists
private_key_path = os.path.join(worker_dir, "private_key.pem")
generate_private_key(private_key_path)