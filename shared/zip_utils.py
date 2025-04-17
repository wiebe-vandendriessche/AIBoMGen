import zipfile
import os
import shutil

MAX_ZIP_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_TOTAL_UNCOMPRESSED_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
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
        total_uncompressed_size = 0

        for member in zip_ref.infolist():
            # Prevent path traversal
            member_path = os.path.realpath(os.path.join(extract_to, member.filename))
            if not member_path.startswith(os.path.realpath(extract_to)):
                raise ZipValidationError("Path traversal detected in .zip file!")

            # Skip directories (only validate files)
            if member.is_dir():
                continue

            # Check file extensions
            if not os.path.splitext(member.filename)[1].lower() in ALLOWED_EXTENSIONS:
                raise ZipValidationError(f"Invalid file type in .zip file: {member.filename}")

            # Check individual file size
            if member.file_size > MAX_FILE_SIZE:
                raise ZipValidationError(f"File {member.filename} exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes.")

            # Accumulate total uncompressed size
            total_uncompressed_size += member.file_size
            if total_uncompressed_size > MAX_TOTAL_UNCOMPRESSED_SIZE:
                raise ZipValidationError("The total uncompressed size of the .zip file exceeds the allowed limit.")

        # Extract files
        zip_ref.extractall(extract_to)