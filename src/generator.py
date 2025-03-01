import os
from datetime import datetime
import extractors.environment_info
import extractors.installed_packages
import extractors.docker_image_details
import extractors.mounted_data_access
import extractors.gpu_info
import json
import docker
import re
import time
import threading
import cyclonedx_generator
import mlflow
from mlflow.tracking import MlflowClient

client = docker.from_env()

# Global AIBoM dictionary
aibom = {}

def collect_initial_aibom_data(dockerfile_path, output_folder, project_root, container_id, mounted_data_abs):
    """
    Collect initial data (environment info and installed packages) as soon as the container starts.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    container = client.containers.get(container_id)

    # Extract environment and installed packages before training
    installed_packages = extractors.installed_packages.extract_installed_packages(container)
    environment_info = extractors.environment_info.extract_environment_info(container)
    docker_image_details = extractors.docker_image_details.extract_docker_image_details(dockerfile_path)
    gpu_info = extractors.gpu_info.extract_gpu_info(container)

    # Initialize the AIBoM with start data
    aibom.update({
        "start": timestamp,
        "installed_packages": installed_packages,
        "docker_image": docker_image_details,
        "environment_info": environment_info,
        "gpu_info": gpu_info  # Collect GPU data at the start
    })

    # Start monitoring file accesses in the background (use the mount point you want to track)
    mount_point = "/user_mounted_data/mnist_data"  # Replace with the path of your mounted data
    file_access_thread = threading.Thread(
        target=extractors.mounted_data_access.monitor_file_access_in_container,
        args=(container, mount_point, lambda log: extractors.mounted_data_access.log_file_access(log, aibom, mount_point, container, mounted_data_abs))
    )
    file_access_thread.start()


def generate_aibom_after_training(dockerfile_path, output_folder, project_root, container_id):
    """
    Generate the AIBoM after training has completed (logs, model details, etc.).
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    container = client.containers.get(container_id)

    # Extract training logs
    training_logs = container.logs().decode()
    progress_bar_pattern = r"\[=[\s=]+\]"
    filtered_logs = []
    for line in training_logs.splitlines():
        if re.search(progress_bar_pattern, line):
            filtered_logs.append(line)

    # Update AIBoM with the final data
    aibom.update({
        "end": timestamp,
        "training_logs": filtered_logs,
        # Add other final data here (like model details, etc.)
    })

    # Retrieve MLflow data during training (while the container is running)
    # Retrieve MLflow data from the log files in the output folder
    mlflow_data = read_mlflow_data_from_logs(output_folder)
    if mlflow_data:
        add_mlflow_data_to_aibom(mlflow_data)


    cyclonedx_generator.generate_cyclonedx_format(aibom, output_folder)

def read_mlflow_data_from_logs(output_folder):
    """
    Reads MLflow data (logs) from the output folder.
    """
    mlflow_data = {}

    try:
        with open(os.path.join(output_folder, 'training_output.log'), 'r') as log_file:
            # Add logic to extract relevant data from the logs if necessary
            mlflow_data['output'] = log_file.read()

        with open(os.path.join(output_folder, 'training_errors.log'), 'r') as error_file:
            # Add logic to extract relevant data from the error logs if necessary
            mlflow_data['errors'] = error_file.read()

    except FileNotFoundError as e:
        print(f"Error reading MLflow log files: {e}")

    return mlflow_data


def add_mlflow_data_to_aibom(mlflow_data):
    """
    Adds MLflow log data to the AIBoM.
    """
    if mlflow_data:
        if 'output' in mlflow_data:
            aibom["mlflow_output"] = mlflow_data['output']

        if 'errors' in mlflow_data:
            aibom["mlflow_errors"] = mlflow_data['errors']

    print("MLflow data added to AIBoM.")
