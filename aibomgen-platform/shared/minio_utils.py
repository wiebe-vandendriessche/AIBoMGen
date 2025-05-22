import boto3
import os
from botocore.exceptions import NoCredentialsError

# Load environment variables
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")

# Define bucket names
TRAINING_BUCKET = os.getenv("TRAINING_BUCKET", "training-jobs")
WORKER_SCANS_BUCKET = os.getenv("WORKER_SCANS_BUCKET", "worker-scans")
SCANNER_SCANS_BUCKET = os.getenv("SCANNER_SCANS_BUCKET", "scanner-scans")

# Initialize MinIO client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)


def upload_file_to_minio(file_path, object_name, bucket_name):
    """Upload a file to a specific MinIO bucket."""
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        return f"{MINIO_ENDPOINT}/{bucket_name}/{object_name}"
    except NoCredentialsError:
        raise Exception("MinIO credentials not available")
    except Exception as e:
        raise Exception(f"Failed to upload file to MinIO: {str(e)}")


def download_file_from_minio(object_name, download_path, bucket_name):
    """Download a file from a specific MinIO bucket."""
    try:
        s3_client.download_file(bucket_name, object_name, download_path)
    except Exception as e:
        raise Exception(f"Failed to download file from MinIO: {str(e)}")


def remove_file_from_minio(object_name, bucket_name):
    """Remove a file from a specific MinIO bucket."""
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
    except FileNotFoundError:
        raise Exception(
            f"The object {object_name} does not exist in bucket {bucket_name}.")
    except Exception as e:
        raise Exception(f"Failed to remove file from MinIO: {str(e)}")


def create_bucket_if_not_exists():
    """Ensure all predefined buckets in MinIO are created."""
    bucket_names = [TRAINING_BUCKET, WORKER_SCANS_BUCKET, SCANNER_SCANS_BUCKET]
    for bucket_name in bucket_names:
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except Exception:
            s3_client.create_bucket(Bucket=bucket_name)


def list_files_in_bucket(prefix, bucket_name):
    """List all files in a specific directory (prefix) in a bucket."""
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
        return []
    except Exception as e:
        raise Exception(f"Failed to list files in bucket: {str(e)}")


def generate_presigned_url(object_name, bucket_name, expiration=3600):
    """Generate a presigned URL for a file in a specific MinIO bucket."""
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
        return url
    except Exception as e:
        raise Exception(f"Failed to generate presigned URL: {str(e)}")
