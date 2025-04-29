import platform
import os
import time
import psutil
from celery import current_task
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetCount, nvmlDeviceGetName, nvmlDeviceGetMemoryInfo, nvmlShutdown
import docker
import subprocess
import json
from shared.minio_utils import upload_file_to_minio

def extract_environment_details(task_logger, unique_dir, start_task_time, start_training_time, start_aibom_time):
    """
    Extract useful environment details for the training process, including GPU, Celery, Docker, and vulnerability information.

    Args:
        task_logger (Logger): Logger for logging task-specific information.
        unique_dir (str): Unique directory for the task.
        start_task_time (float): Task start time in seconds since epoch.
        start_training_time (float): Training start time in seconds since epoch.
        start_aibom_time (float): AIBoM generation start time in seconds since epoch.

    Returns:
        dict: A dictionary containing environment details.
    """
    try:
        task_logger.info("Extracting environment details...")

        # Extract details
        os_info = platform.system() + " " + platform.release()
        python_version = platform.python_version()
        tensorflow_version = get_tensorflow_version()
        cpu_count = psutil.cpu_count(logical=True)
        memory_total = psutil.virtual_memory().total // (1024 * 1024)  # in MB
        disk_usage = psutil.disk_usage('/').total // (1024 * 1024)  # in MB
        gpu_info = get_gpu_info(task_logger=task_logger)
        celery_task_info = get_celery_task_info(task_logger=task_logger)
        docker_info = get_docker_info(task_logger=task_logger)
        vulnerability_scan = scan_container_vulnerabilities_with_trivy(unique_dir=unique_dir ,task_logger=task_logger, docker_info=docker_info)
        
        task_logger.info("Environment details extracted successfully.")

        return {
            "os": os_info,
            "python_version": python_version,
            "tensorflow_version": tensorflow_version,
            "cpu_count": cpu_count,
            "memory_total": memory_total,
            "disk_usage": disk_usage,
            "gpu_info": gpu_info,
            "celery_task_info": celery_task_info,
            "docker_info": docker_info,
            "vulnerability_scan": vulnerability_scan,
            "request_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_task_time)),
            "start_training_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_training_time)),
            "start_aibom_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_aibom_time)),
            "training_time": start_aibom_time - start_training_time,
            "job_id": current_task.request.id if current_task else "Unknown",
            "unique_dir": unique_dir,
        }
    except Exception as e:
        task_logger.error(f"An error occurred while extracting environment details: {str(e)}")
        raise
    
def get_tensorflow_version(task_logger=None):
    """
    Get the installed TensorFlow version.

    Args:
        task_logger (Logger, optional): Logger for logging task-specific information.

    Returns:
        str: TensorFlow version or 'Unknown' if not installed.
    """
    try:
        if task_logger:
            task_logger.info("Retrieving TensorFlow version...")
        import tensorflow as tf
        version = tf.__version__
        if task_logger:
            task_logger.info(f"TensorFlow version retrieved: {version}")
        return version
    except ImportError:
        if task_logger:
            task_logger.warning("TensorFlow is not installed.")
        return "Unknown"
    except Exception as e:
        if task_logger:
            task_logger.error(f"Error retrieving TensorFlow version: {str(e)}")
        return "Unknown"
    
def get_gpu_info(task_logger=None):
    """
    Get GPU information using NVIDIA's NVML library.

    Args:
        task_logger (Logger, optional): Logger for logging task-specific information.

    Returns:
        list: A list of dictionaries containing GPU details or 'No GPU detected' if no GPU is available.
    """
    try:
        if task_logger:
            task_logger.info("Retrieving GPU information...")
        nvmlInit()
        gpus = []
        device_count = nvmlDeviceGetCount()  # Get the number of GPUs
        for i in range(device_count):
            handle = nvmlDeviceGetHandleByIndex(i)
            name = nvmlDeviceGetName(handle).decode("utf-8")
            memory_info = nvmlDeviceGetMemoryInfo(handle)
            gpus.append({
                "name": name,
                "memory_total": memory_info.total // (1024 * 1024),  # in MB
                "memory_used": memory_info.used // (1024 * 1024),    # in MB
            })
        nvmlShutdown()
        if task_logger:
            task_logger.info("GPU information retrieved successfully.")
        return gpus
    except Exception as e:
        if task_logger:
            task_logger.error(f"Error retrieving GPU info: {str(e)}")
        return f"Error retrieving GPU info: {str(e)}"
    
def get_docker_info(task_logger=None):
    """
    Get Docker container and image information using the Docker SDK.

    Args:
        task_logger (Logger, optional): Logger for logging task-specific information.

    Returns:
        dict: Docker details or 'Not running in a Docker container' if not applicable.
    """
    try:
        if task_logger:
            task_logger.info("Retrieving Docker container and image information...")
        # Check if running inside a Docker container
        if os.path.exists("/.dockerenv"):
            client = docker.from_env()
            container_id = os.getenv("HOSTNAME", "Unknown")
            container = client.containers.get(container_id)
            image = container.image
            docker_info = {
                "container_id": container_id,
                "image_name": image.tags[0] if image.tags else "Unknown",
                "image_id": image.id,
            }
            if task_logger:
                task_logger.info(f"Docker information retrieved: {docker_info}")
            return docker_info
        else:
            if task_logger:
                task_logger.warning("Not running in a Docker container.")
            return "Not running in a Docker container"
    except docker.errors.DockerException as e:
        if task_logger:
            task_logger.error(f"Docker daemon is not accessible: {str(e)}")
        return f"Error retrieving Docker info: {str(e)}"
    except Exception as e:
        if task_logger:
            task_logger.error(f"Error retrieving Docker info: {str(e)}")
        return f"Error retrieving Docker info: {str(e)}"

    
def get_celery_task_info(task_logger=None):
    """
    Get information about the current Celery task.

    Args:
        task_logger (Logger, optional): Logger for logging task-specific information.

    Returns:
        dict: Celery task details or 'Unknown' if not running in a Celery task.
    """
    try:
        if task_logger:
            task_logger.info("Retrieving Celery task information...")
        if current_task:
            task_info = {
                "task_id": current_task.request.id,
                "task_name": current_task.name,
                "queue": current_task.request.delivery_info.get("routing_key", "Unknown"),
            }
            if task_logger:
                task_logger.info(f"Celery task information retrieved: {task_info}")
            return task_info
        else:
            if task_logger:
                task_logger.warning("Not running in a Celery task.")
            return "Not running in a Celery task"
    except Exception as e:
        if task_logger:
            task_logger.error(f"Error retrieving Celery task info: {str(e)}")
        return f"Error retrieving Celery task info: {str(e)}"
    
def scan_container_vulnerabilities_with_trivy(unique_dir, docker_info, task_logger=None):
    """
    Scan the specified Docker image for vulnerabilities using Trivy.

    Args:
        docker_info (dict): Docker container and image information.
        task_logger (Logger, optional): Logger for logging task-specific information.

    Returns:
        dict: A dictionary containing vulnerabilities classified by severity or metadata if no vulnerabilities are found.
    """
    try:
        if task_logger:
            task_logger.info("Scanning container for vulnerabilities using Trivy...")

        # Ensure the image name is available
        image_name = docker_info.get("image_name")
        if not image_name or image_name == "Unknown":
            if task_logger:
                task_logger.error("Docker image name is not available.")
            return {"error": "Docker image name is not available."}

        # Run Trivy using its official container image
        trivy_result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", "/var/run/docker.sock:/var/run/docker.sock",
                "-v", f"{os.path.expanduser('~')}/.cache/trivy:/root/.cache/",
                "aquasec/trivy:latest", "image", "--scanners", "vuln", "--format", "json", image_name
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # Suppress Trivy logs from being passed to worker logs
            text=True,
        )
        if trivy_result.returncode != 0:
            if task_logger:
                task_logger.error(f"Trivy scan failed: {trivy_result.stderr.strip()}")
            return {"error": f"Trivy scan failed: {trivy_result.stderr.strip()}"}

        # Parse the JSON output
        vulnerabilities = json.loads(trivy_result.stdout)
        
        # Summarize vulnerabilities by severity
        summary = {}
        for result in vulnerabilities.get("Results", []):
            for vuln in result.get("Vulnerabilities", []):
                severity = vuln.get("Severity", "UNKNOWN")
                summary[severity] = summary.get(severity, 0) + 1

        # Save the full results to a writable directory (e.g., /tmp)
        output_file = f"/tmp/{image_name.replace(':', '_')}_vulnerabilities.json"
        with open(output_file, "w") as f:
            json.dump(vulnerabilities, f, indent=4)

        if task_logger:
            task_logger.info(f"Full vulnerability scan saved to {output_file}")
        
        # Upload the file to Minio
        upload_file_to_minio(
            file_path=output_file,
            object_name=f"{unique_dir}/output/{os.path.basename(output_file)}",
        )
        
        
        if task_logger:
            task_logger.info("Vulnerability scan completed successfully.")
        return summary

    except FileNotFoundError:
        if task_logger:
            task_logger.error("Docker CLI is not available.")
        return {"error": "Docker CLI is not available."}
    except Exception as e:
        if task_logger:
            task_logger.error(f"An error occurred while scanning for vulnerabilities: {str(e)}")
        return {"error": f"An error occurred while scanning for vulnerabilities: {str(e)}"}


