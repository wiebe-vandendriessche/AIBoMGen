from in_toto.models.metadata import Metablock
from in_toto.models.link import Link
from securesystemslib.signer import CryptoSigner
from securesystemslib.signer._key import SSlibKey
import json
import hashlib
import os

def load_signer(private_key_path, public_key_path):
    """
    Load the private key and public key to recreate a CryptoSigner object.

    Args:
        private_key_path (str): Path to the private key file.
        public_key_path (str): Path to the public key JSON file.

    Returns:
        CryptoSigner: A signer object for the private key.
    """
    # Load the public key from the JSON file
    with open(public_key_path, "r") as pub_file:
        public_key_dict = json.load(pub_file)
        public_key = SSlibKey.from_dict(public_key_dict["keyid"], public_key_dict)

    # Load the private key
    signer = CryptoSigner.from_priv_key_uri(f"file2://{private_key_path}", public_key)
    return signer


def record_artifact_as_dict(file_path):
    """
    Record an artifact as a dictionary with its hash.

    Args:
        file_path (str): Path to the artifact file.

    Returns:
        dict: A dictionary containing the hash of the artifact.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Compute the SHA256 hash of the file
    hash_algorithm = "sha256"
    hash_digest = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_digest.update(chunk)

    return {hash_algorithm: hash_digest.hexdigest()}