import os
from datetime import datetime
import extractors.training_data
import extractors.environment_info
import extractors.installed_packages
import extractors.docker_image_details
import extractors.model_detail
import json

def generate_aibom(dockerfile_path,output_folder, project_root):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Use a timezone-aware timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Automatically extract details from the train.py file
    train_file = os.path.join(project_root, "test", "train.py")

    # Extract details from the train.py file
    training_data = extractors.training_data.extract_training_data(train_file)
    model_architecture, hyperparameters = extractors.model_detail.extract_model_details(train_file)

    # Collect installed packages in the environment (dependencies for the training process)
    installed_packages = extractors.installed_packages.get_installed_packages()

    # Extract Docker image details from the Dockerfile
    docker_image_details = extractors.docker_image_details.extract_docker_image_details(dockerfile_path)

    # Collect environment details (like Python version, OS)
    environment_info = extractors.environment_info.get_environment_info()

    # Create the AIBoM dictionary
    aibom = {
        "training_data": training_data,
        "model": model_architecture,
        "hyperparameters": hyperparameters,
        "timestamp": timestamp,
        "dependencies": installed_packages,
        "docker_image": docker_image_details,
        "environment": environment_info
    }

    # Save the AIBoM as a JSON file in the output folder
    aibom_file_path = os.path.join(output_folder, "aibom.json")
    with open(aibom_file_path, "w") as f:
        json.dump(aibom, f, indent=4)

    print(f"AIBoM generated at {aibom_file_path}")