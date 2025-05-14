from fastapi import APIRouter, UploadFile, HTTPException, File
import os
import json
import base64
from fastapi.responses import JSONResponse
from in_toto.models.metadata import Metablock
from in_toto.verifylib import in_toto_verify
from in_toto.exceptions import (
    SignatureVerificationError,
    LayoutExpiredError,
    LinkNotFoundError,
    ThresholdVerificationError,
    RuleVerificationError,
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from cyclonedx.model.bom import Bom
from cyclonedx.validation.json import JsonStrictValidator
from cyclonedx.schema import SchemaVersion
from cyclonedx.output.json import JsonV1Dot6
from shared.minio_utils import download_file_from_minio, TRAINING_BUCKET
from shared.in_toto_utils import record_artifact_as_dict

# === Router Setup ===
verifier_router = APIRouter(prefix="/verifier", tags=["Verifier Endpoints"])

# === Verifier Endpoints ===


@verifier_router.post("/verify_in-toto_link")
async def verify_in_toto(
    link_file: UploadFile = File(
        ..., description="In-toto link file (e.g., run_training.<keyid>.link)"),
):
    try:
        # Save the uploaded link file temporarily
        temp_dir = "/tmp/verify"
        link_path = save_uploaded_file(link_file, temp_dir)

        # Use the helper function to verify the .link file
        verify_link_file(link_path, temp_dir)

        return {
            "status": "success",
            "message": "Verification successful.",
            "details": {
                "layout_signature": "Verified",
                "layout_expiration": "Valid",
                "link_signatures": "Verified",
                "threshold_verification": "Met",
                "artifact_rules": "All rules satisfied",
            },
        }

    except SignatureVerificationError:
        raise HTTPException(
            status_code=400, detail="Verification failed: Invalid signature on the layout or link file.")
    except LayoutExpiredError:
        raise HTTPException(
            status_code=400, detail="Verification failed: The layout has expired.")
    except LinkNotFoundError:
        raise HTTPException(
            status_code=400, detail="Verification failed: No valid link files found for the step.")
    except ThresholdVerificationError:
        raise HTTPException(
            status_code=400, detail="Verification failed: Threshold requirements not met for the step.")
    except RuleVerificationError as e:
        raise HTTPException(
            status_code=400, detail=f"Verification failed: Artifact rule violation. {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Verification failed: {str(e)}")


@verifier_router.post("/verify_file_hash")
async def verify_file_hash(
    link_file: UploadFile = File(
        ..., description="In-toto link file (e.g., run_training.<keyid>.link)"),
    uploaded_file: UploadFile = File(
        ..., description="File to verify (e.g., a model or metrics file)."),
):
    """
    Verify the hash of an uploaded file against the in-toto link file metadata.
    """
    try:
        # Save the uploaded files temporarily
        temp_dir = "/tmp/verify"
        link_path = save_uploaded_file(link_file, temp_dir)
        file_to_verify_path = save_uploaded_file(uploaded_file, temp_dir)

        # Load the link file
        link_metadata = Metablock.load(link_path)

        # Compute the hash of the uploaded file
        computed_hash = record_artifact_as_dict(file_to_verify_path)

        # Check if the hash matches any material or product in the link file
        recorded_hash = None
        for path, hash_dict in {**link_metadata.signed.materials, **link_metadata.signed.products}.items():
            if os.path.basename(path) == uploaded_file.filename:
                recorded_hash = hash_dict
                break

        if not recorded_hash:
            raise HTTPException(
                status_code=404,
                detail=f"File '{uploaded_file.filename}' not found in materials or products of the link file.",
            )

        # Compare the hashes
        if computed_hash != recorded_hash:
            return {
                "status": "failure",
                "message": "Hash mismatch.",
                "details": {
                    "file_name": uploaded_file.filename,
                    "computed_hash": computed_hash,
                    "recorded_hash": recorded_hash,
                },
            }

        return {
            "status": "success",
            "message": "Hash matches the recorded metadata.",
            "details": {
                "file_name": uploaded_file.filename,
                "hash": computed_hash,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Verification failed: {str(e)}")


@verifier_router.post("/verify_minio_artifacts")
async def verify_minio_artifacts(
    link_file: UploadFile = File(
        ..., description="In-toto link file (e.g., run_training.<keyid>.link)"),
):
    """
    Verify materials and products stored in MinIO against the in-toto link file metadata.
    If this has mismatches, this means that the artifacts in MinIO are not the same as those recorded in the link file.
    This could be due to a malicious actor that has access to MinIO tampering with the files.
    Because the link file is signed, the malicious actor cannot change the link file itself to match the tampered files.
    """
    try:
        # Save the uploaded link file temporarily
        temp_dir = "/tmp/verify"
        link_path = save_uploaded_file(link_file, temp_dir)

        # Load the link file
        link_metadata = Metablock.load(link_path)

        # Prepare to store verification results
        mismatched_materials = []
        mismatched_products = []
        verified_materials = []
        verified_products = []

        # Extract unique_dir dynamically from the first material or product path
        all_paths = list(link_metadata.signed.materials.keys()) + \
            list(link_metadata.signed.products.keys())
        if not all_paths:
            raise HTTPException(
                status_code=400, detail="No materials or products found in the link file.")

        # Assume the unique_dir is the first part of the path (e.g., "2809d3f5-72d8-4097-932c-401f3433c255")
        unique_dir = all_paths[0].split("/")[0]

        # Verify materials
        for material_path, recorded_hash in link_metadata.signed.materials.items():
            minio_path = material_path  # Full path already includes unique_dir
            local_path = os.path.join(
                temp_dir, os.path.basename(material_path))

            # Download material from MinIO
            try:
                download_file_from_minio(
                    minio_path, local_path, TRAINING_BUCKET)
            except Exception as e:
                mismatched_materials.append({
                    "path": material_path,
                    "error": f"Failed to download from MinIO: {str(e)}"
                })
                continue

            # Compute hash and compare
            computed_hash = record_artifact_as_dict(local_path)
            if computed_hash != recorded_hash:
                mismatched_materials.append({
                    "path": material_path,
                    "computed_hash": computed_hash,
                    "recorded_hash": recorded_hash,
                })
            else:
                verified_materials.append(material_path)

        # Verify products
        for product_path, recorded_hash in link_metadata.signed.products.items():
            minio_path = product_path  # Full path already includes unique_dir
            local_path = os.path.join(temp_dir, os.path.basename(product_path))

            # Download product from MinIO
            try:
                download_file_from_minio(
                    minio_path, local_path, TRAINING_BUCKET)
            except Exception as e:
                mismatched_products.append({
                    "path": product_path,
                    "error": f"Failed to download from MinIO: {str(e)}"
                })
                continue

            # Compute hash and compare
            computed_hash = record_artifact_as_dict(local_path)
            if computed_hash != recorded_hash:
                mismatched_products.append({
                    "path": product_path,
                    "computed_hash": computed_hash,
                    "recorded_hash": recorded_hash,
                })
            else:
                verified_products.append(product_path)

        # Prepare response
        response = {
            "status": "success" if not mismatched_materials and not mismatched_products else "failure",
            "verified_materials": verified_materials,
            "verified_products": verified_products,
            "mismatched_materials": mismatched_materials,
            "mismatched_products": mismatched_products,
        }

        return response

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Verification failed: {str(e)}")


@verifier_router.post("/verify_bom_and_link")
async def verify_bom_and_link(
    bom_file: UploadFile = File(...,
                                description="A signed CycloneDX BOM file (JSON format)."),
):
    try:
        # Save the BOM file
        temp_dir = "/tmp/verify"
        bom_path = save_uploaded_file(bom_file, temp_dir)

        # Load the BOM file content
        with open(bom_path, "r") as f:
            bom_data = f.read()

        # Validate the BOM against the CycloneDX schema
        validator = JsonStrictValidator(SchemaVersion.V1_6)
        validation_errors = validator.validate_str(bom_data)
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail=f"BOM validation failed: {repr(validation_errors)}"
            )

        # Deserialize the BOM to extract the signature and serialized content
        bom = Bom.from_json(json.loads(bom_data))

        # Extract the signature from the BOM metadata
        signature_property = next(
            (prop for prop in bom.metadata.properties if prop.name ==
             "BOM Signature"), None
        )
        if not signature_property:
            raise HTTPException(
                status_code=400, detail="BOM signature not found in metadata.")

        # Decode the signature from Base64
        signature_bytes = base64.b64decode(signature_property.value)

        # Remove the BOM Signature property and timestamp for verification
        bom.metadata.properties = [
            prop for prop in bom.metadata.properties if prop.name != "BOM Signature"
        ]
        bom.metadata.timestamp = None

        # Serialize the BOM to JSON (excluding the BOM Signature property)
        json_outputter = JsonV1Dot6(bom)
        serialized_bom = json_outputter.output_as_string(indent=4)

        # Load the worker's public key
        public_key_bytes = load_worker_public_key()

        # Verify the BOM signature using cryptography's Ed25519 module
        try:
            public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
            public_key.verify(signature_bytes, serialized_bom.encode("utf-8"))
        except InvalidSignature:
            raise HTTPException(
                status_code=400, detail="BOM signature verification failed.")

        # Extract the .link file reference from the BOM
        link_reference = next(
            (str(ref.url) for ref in bom.external_references
             if ref.type == "attestation" and ref.comment == "in-toto .link file for artifact integrity verification"),
            None
        )
        if not link_reference:
            raise HTTPException(
                status_code=400, detail="No .link file reference found in BOM.")

        # Verify the .link file
        link_path = os.path.join(temp_dir, os.path.basename(link_reference))
        download_file_from_minio(link_reference, link_path, TRAINING_BUCKET)

        try:
            verify_link_file(link_path, temp_dir)
        except SignatureVerificationError:
            raise HTTPException(
                status_code=400, detail="Verification failed: Invalid signature on the layout or link file.")
        except LayoutExpiredError:
            raise HTTPException(
                status_code=400, detail="Verification failed: The layout has expired.")
        except LinkNotFoundError:
            raise HTTPException(
                status_code=400, detail="Verification failed: No valid link files found for the step.")
        except ThresholdVerificationError:
            raise HTTPException(
                status_code=400, detail="Verification failed: Threshold requirements not met for the step.")
        except RuleVerificationError as e:
            raise HTTPException(
                status_code=400, detail=f"Verification failed: Artifact rule violation. {str(e)}")
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Verification failed during .link file verification: {str(e)}")

        return JSONResponse(
            content={
                "status": "success",
                "message": "BOM and .link file verification successful.",
                "details": {
                    "bom_signature": "Verified",
                    "link_file": "Verified",
                },
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Verification failed: {str(e)}")


def verify_link_file(link_path: str, temp_dir: str):
    """
    Helper function to verify an in-toto .link file against the signed layout.
    """
    # Path to the signed layout file (assumed to be in /run/secrets)
    layout_path = "/run/secrets/signed_layout"

    # Check if the signed layout file exists
    if not os.path.exists(layout_path):
        raise HTTPException(
            status_code=500,
            detail="The signed layout file does not exist. Please ensure it is available at '/run/secrets/signed_layout'.",
        )

    # Load the signed layout and the .link file
    layout_metadata = Metablock.load(layout_path)
    link_metadata = Metablock.load(link_path)

    # Verify the .link file
    in_toto_verify(
        metadata=layout_metadata,
        layout_key_dict=layout_metadata.signed.keys,
        link_dir_path=temp_dir,
    )


def load_worker_public_key(worker_public_key_path: str = "/run/secrets/worker_public_key") -> bytes:
    """
    Load and validate the worker's public key from a JSON file.
    """
    if not os.path.exists(worker_public_key_path):
        raise HTTPException(
            status_code=500,
            detail="Worker public key not found. Please ensure it is available at the specified path.",
        )

    with open(worker_public_key_path, "r") as f:
        public_key_data = json.load(f)

    if public_key_data["keytype"] != "ed25519" or public_key_data["scheme"] != "ed25519":
        raise HTTPException(
            status_code=400,
            detail="Invalid public key format. Expected Ed25519 key.",
        )

    public_key_hex = public_key_data["keyval"]["public"]
    return bytes.fromhex(public_key_hex)


def save_uploaded_file(uploaded_file: UploadFile, temp_dir: str) -> str:
    """
    Save an uploaded file to a temporary directory and return its path.
    """
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, uploaded_file.filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.file.read())
    return file_path
