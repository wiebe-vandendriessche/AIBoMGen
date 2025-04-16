import boto3
import os
from botocore.exceptions import NoCredentialsError

# Load environment variables
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

# Initialize MinIO client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

def upload_file_to_minio(file_path, object_name):
    """Upload a file to MinIO."""
    try:
        s3_client.upload_file(file_path, MINIO_BUCKET_NAME, object_name)
        return f"{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/{object_name}"
    except NoCredentialsError:
        raise Exception("MinIO credentials not available")
    except Exception as e:
        raise Exception(f"Failed to upload file to MinIO: {str(e)}")

def download_file_from_minio(object_name, download_path):
    """Download a file from MinIO."""
    try:
        s3_client.download_file(MINIO_BUCKET_NAME, object_name, download_path)
    except Exception as e:
        raise Exception(f"Failed to download file from MinIO: {str(e)}")

def create_bucket_if_not_exists():
    """Create the bucket in MinIO if it doesn't already exist."""
    try:
        s3_client.head_bucket(Bucket=MINIO_BUCKET_NAME)
    except Exception:
        s3_client.create_bucket(Bucket=MINIO_BUCKET_NAME)
        
def list_files_in_bucket(prefix):
    """List all files in a specific directory (prefix) in the bucket."""
    try:
        response = s3_client.list_objects_v2(Bucket=MINIO_BUCKET_NAME, Prefix=prefix)
        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
        return []
    except Exception as e:
        raise Exception(f"Failed to list files in bucket: {str(e)}")
    
def generate_presigned_url(object_name, expiration=3600):
    """Generate a presigned URL for a file in MinIO."""
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": MINIO_BUCKET_NAME, "Key": object_name},
            ExpiresIn=expiration,
        )
        return url
    except Exception as e:
        raise Exception(f"Failed to generate presigned URL: {str(e)}")