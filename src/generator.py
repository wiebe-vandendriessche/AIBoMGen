import os
from datetime import datetime
import extractors.training_data
import extractors.environment_info
import extractors.installed_packages
import extractors.docker_image_details
import extractors.model_detail
import json
import docker
import re

client = docker.from_env()

def generate_aibom(dockerfile_path,output_folder, project_root, container_id):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    container = client.containers.get(container_id)

    training_logs = container.logs().decode()
    progress_bar_pattern = r"\[=[\s=]+\]"
    filtered_logs = []
    for line in training_logs.splitlines():
        if re.search(progress_bar_pattern, line):
            filtered_logs.append(line)


    installed_packages = extractors.installed_packages.extract_installed_packages(container)
    environment_info = extractors.environment_info.extract_environment_info(container)
    docker_image_details = extractors.docker_image_details.extract_docker_image_details(dockerfile_path)

    # Create a temporary AIBoM
    aibom = {
        "timestamp": timestamp,
        "training_logs": filtered_logs,
        "dependencies": installed_packages,
        "docker_image": docker_image_details,
        "environment": environment_info
    }

    # Save the AIBoM as a JSON file in the output folder
    aibom_file_path = os.path.join(output_folder, "aibom.json")
    with open(aibom_file_path, "w") as f:
        json.dump(aibom, f, indent=4)

    print(f"AIBoM generated at {aibom_file_path}")