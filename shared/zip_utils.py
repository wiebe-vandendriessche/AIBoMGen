import zipfile
import os
import shutil

MAX_ZIP_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {".jpg", ".png", ".csv"}

class ZipValidationError(Exception):
    """Custom exception for zip validation errors."""
    pass

def validate_zip_file(zip_path):
    """Validate the .zip file for size and structure."""
    # Check file size
    if os.path.getsize(zip_path) > MAX_ZIP_FILE_SIZE:
        raise ZipValidationError("Uploaded .zip file is too large.")

    # Check if it's a valid .zip file
    if not zipfile.is_zipfile(zip_path):
        raise ZipValidationError("Uploaded file is not a valid .zip archive.")

def validate_and_extract_zip(zip_path, extract_to):
    """Validate and safely extract a .zip file."""
    validate_zip_file(zip_path)  # Perform basic validation

    # Extract safely
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            # Prevent path traversal
            member_path = os.path.join(extract_to, member)
            if not os.path.commonprefix([extract_to, member_path]) == extract_to:
                raise ZipValidationError("Path traversal detected in .zip file!")

            # Skip directories (only validate files)
            if member.endswith('/'):
                continue

            # Check file extensions
            if not os.path.splitext(member)[1].lower() in ALLOWED_EXTENSIONS:
                raise ZipValidationError(f"Invalid file type in .zip file: {member}")

        zip_ref.extractall(extract_to)