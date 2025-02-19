import docker
from docker.errors import APIError

client = docker.from_env()

def extract_gpu_info(container):
    """
    Extract GPU information from a running container by executing the `nvidia-smi` command.
    If no GPU is available, return a statement indicating no GPU usage.
    """
    print("Extracting GPU info from the running container...")

    # Check if `nvidia-smi` is available, which would indicate GPU usage
    try:
        result = container.exec_run("nvidia-smi", stdout=True, stderr=True)

        # Decode the output to capture the GPU info
        gpu_info = result.output.decode().strip()

        if "not found" in gpu_info or "NVIDIA-SMI" not in gpu_info:
            return "No GPU detected. This container is not using a GPU."

        return gpu_info

    except docker.errors.APIError as e:
        # Handle case where `nvidia-smi` is not available
        return "No GPU detected. This container is not using a GPU."
