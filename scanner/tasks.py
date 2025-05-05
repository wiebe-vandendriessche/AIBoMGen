from shared.minio_utils import upload_file_to_minio, create_bucket_if_not_exists, WORKER_SCANS_BUCKET, SCANNER_SCANS_BUCKET
import subprocess
import json
import os
from datetime import datetime
import docker
from celery_config import celery_app

def get_docker_info():
    """
    Dynamically retrieve Docker container and image information.
    """
    try:
        if os.path.exists("/.dockerenv"):
            client = docker.from_env()
            container_id = os.getenv("HOSTNAME", "Unknown")
            container = client.containers.get(container_id)
            image = container.image
            return {
                "container_id": container_id,
                "image_name": image.tags[0] if image.tags else "Unknown",
                "image_id": image.id,
            }
        return {"error": "Not running in a Docker container"}
    except Exception as e:
        return {"error": f"Error retrieving Docker info: {str(e)}"}


@celery_app.task(name="tasks.scan_worker_and_self_images")
def scan_worker_and_self_images():
    """
    Periodically scan both the worker image and the scanner image for vulnerabilities using Trivy,
    and save results to separate buckets in MinIO.
    """
    try:
        # Ensure required buckets exist
        create_bucket_if_not_exists()

        # Retrieve the worker image name from environment variables
        worker_image_name = os.getenv("WORKER_IMAGE_NAME")
        if not worker_image_name:
            raise ValueError("Worker image name is not defined in the environment variables.")

        # Retrieve the scanner image name dynamically
        scanner_image_info = get_docker_info()
        if "error" in scanner_image_info:
            raise ValueError(scanner_image_info["error"])
        scanner_image_name = scanner_image_info.get("image_name")
        if not scanner_image_name or scanner_image_name == "Unknown":
            raise ValueError("Scanner image name could not be determined.")

        # Helper function to perform the scan
        def perform_scan(image_name, bucket_name, bucket_prefix):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"/tmp/{image_name.replace(':', '_')}_vulnerabilities_{timestamp}.json"

            network_name = "internal_network"  # The network name to use for the scan
            container_name = f"trivy_scanner_{timestamp}"  # Unique container name for the scan
    
            # Run Trivy scan in Trivy container
            trivy_result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", "/var/run/docker.sock:/var/run/docker.sock",
                    "-v", f"{os.path.expanduser('~')}/.cache/trivy:/root/.cache/",
                    "aquasec/trivy:latest", "image", "--scanners", "vuln", "--format", "json", image_name
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            if trivy_result.returncode != 0:
                raise Exception(f"Trivy scan failed for {image_name}: {trivy_result.stderr.strip()}")

            # Save results to a file
            vulnerabilities = json.loads(trivy_result.stdout)
            with open(output_file, "w") as f:
                json.dump(vulnerabilities, f, indent=4)

            # Upload to MinIO
            upload_file_to_minio(
                file_path=output_file,
                object_name=f"{bucket_prefix}/{os.path.basename(output_file)}",
                bucket_name=bucket_name,
            )

        # Perform scans for both images
        perform_scan(worker_image_name, WORKER_SCANS_BUCKET, "worker-vulnerability-scans")
        perform_scan(scanner_image_name, SCANNER_SCANS_BUCKET, "scanner-vulnerability-scans")

        return {"status": "success", "message": "Both images scanned and results uploaded to MinIO."}

    except Exception as e:
        return {"status": "error", "message": str(e)}