from in_toto.models.metadata import Metablock
from in_toto.models.link import Link
from securesystemslib.signer import CryptoSigner
from securesystemslib.signer._key import SSlibKey
import json
import hashlib
import os

def generate_in_toto_link(task_name, materials, products, command, signer, link_file_path, task_logger):
    """
    Generate and sign an in-toto link file for a task.

    Args:
        task_name (str): Name of the task (e.g., "run_training").
        materials (dict): Input artifacts (e.g., dataset, model, datasetdefinition).
        products (dict): Output artifacts (e.g., trained model, metrics).
        command (list): Command executed for the task.
        signer (CryptoSigner): CryptoSigner object for signing the link.
        link_file_path (str): Path to save the generated link file.
        task_logger (logging.Logger): Logger for logging messages.
    """
    try:
        # Create the in-toto link metadata
        task_logger.info("Creating in-toto link metadata...")
        link = Link(
            name=task_name,
            materials=materials,
            products=products,
            byproducts={"stdout": "Task completed successfully."},
            command=command,
        )

        # Sign the link with the CryptoSigner
        task_logger.info("Signing in-toto link metadata...")
        link_metadata = Metablock(signed=link)
        link_metadata.create_signature(signer)

        # Save the link metadata to a file
        task_logger.info(f"Saving in-toto link file to: {link_file_path}")
        link_metadata.dump(link_file_path)

        task_logger.info("in-toto link file generated and signed successfully.")
    except Exception as e:
        task_logger.error(f"Failed to generate in-toto link file: {str(e)}")
        raise
        
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

    return {
        file_path: {
            hash_algorithm: hash_digest.hexdigest()
        }
    }