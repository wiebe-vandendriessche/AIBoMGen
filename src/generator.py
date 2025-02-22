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

client = docker.from_env()

# Global AIBoM dictionary
aibom = {}

def is_inotify_installed(container):
    """Check if inotify-tools is installed in the container."""
    try:
        exec_result = container.exec_run("which inotifywait")
        return exec_result.exit_code == 0
    except Exception as e:
        print(f"Error checking for inotify: {e}")
        return False

def monitor_file_access_in_container(container, mount_point, log_callback):
    """Monitor file accesses in the container only if inotify-tools is available."""
    if not is_inotify_installed(container):
        print("Skipping file access monitoring: inotify-tools not found in container.")
        return

    command = f"inotifywait -m {mount_point} -e open -e access"
    try:
        exec_instance = container.exec_run(command, stream=True, stdout=True, stderr=True)
        for line in exec_instance.output:
            decoded_line = line.decode().strip()
            print(f"File accessed: {decoded_line}")
            log_callback(decoded_line)
    except Exception as e:
        print(f"Error monitoring file access: {e}")


def collect_initial_aibom_data(dockerfile_path, output_folder, project_root, container_id):
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
        "dependencies": installed_packages,
        "docker_image": docker_image_details,
        "environment": environment_info,
        "gpu": gpu_info  # Collect GPU data at the start
    })

    # Start monitoring file accesses in the background (use the mount point you want to track)
    mount_point = "/user_mounted_data/mnist_data"  # Replace with the path of your mounted data
    file_access_thread = threading.Thread(target=monitor_file_access_in_container, args=(container, mount_point, log_file_access))
    file_access_thread.start()

def log_file_access(file_access_log):
    """
    Log file access into the AIBoM dictionary.
    """
    print(f"Logging file access: {file_access_log}")  # Add this log
    if "file_access_logs" not in aibom:
        aibom["file_access_logs"] = []
    aibom["file_access_logs"].append(file_access_log)


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

    # Save the final AIBoM as a JSON file in the output folder
    aibom_file_path = os.path.join(output_folder, "aibom.json")
    with open(aibom_file_path, "w") as f:
        json.dump(aibom, f, indent=4)

    print(f"Final AIBoM generated at {aibom_file_path}")
