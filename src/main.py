import docker
import subprocess
import os
import json
import time
from datetime import datetime, timezone
import importlib.resources
import ast

def run_user_docker_container(dockerfile_path, output_folder):
    # Determine the project root directory (one level above src)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Construct the absolute path to the Dockerfile
    dockerfile_abs = os.path.join(project_root, dockerfile_path)
    print(f"Building Docker image from {dockerfile_abs}")

    # Build the Docker image using the project root as the build context
    subprocess.run(
        ["docker", "build", "-t", "user-ai-image", "-f", dockerfile_abs, "."],
        cwd=project_root
    )

    # Absolute path to the output folder in the project root
    output_folder_absolute = os.path.join(project_root, output_folder)

    # Run the Docker container and mount the output folder
    print("Starting Docker container with user's training code...")
    subprocess.Popen(
        ["docker", "run", "--rm", "-v", f"{output_folder_absolute}:/output", "user-ai-image"],
        cwd=project_root
    )

    # Generate the AIBoM
    print("Generating AIBoM...")
    generate_aibom(output_folder_absolute, dockerfile_abs, project_root)


def generate_aibom(output_folder_absolute, dockerfile_abs, project_root):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder_absolute):
        os.makedirs(output_folder_absolute)

    # Use a timezone-aware timestamp (UTC)
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    # Automatically extract details from the train.py file
    train_file = os.path.join(project_root, "test", "train.py")

    # Extract details from the train.py file
    training_data = extract_training_data(train_file)
    model_architecture, hyperparameters = extract_model_details(train_file)

    # Collect installed packages in the environment (dependencies for the training process)
    installed_packages = get_installed_packages()

    # Extract Docker image details from the Dockerfile
    docker_image_details = extract_docker_image_details(dockerfile_abs)

    # Collect environment details (like Python version, OS)
    environment_info = get_environment_info()

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
    aibom_file_path = os.path.join(output_folder_absolute, "aibom.json")
    with open(aibom_file_path, "w") as f:
        json.dump(aibom, f, indent=4)

    print(f"AIBoM generated at {aibom_file_path}")

def extract_training_data(train_file):
    # Open and parse the train.py file
    with open(train_file, "r") as f:
        script_content = f.read()

    # Search for common data loading patterns (for example, PyTorch or TensorFlow datasets)
    data_info = {}
    if "torchvision" in script_content:
        # Attempt to identify the dataset used in PyTorch
        data_info = {
            "framework": "PyTorch",
            "dataset": "CIFAR-10",  # Ideally, dynamically find this
            "source": "https://pytorch.org/vision/stable/transforms.html"
        }
    elif "tensorflow" in script_content:
        # Attempt to identify the dataset used in TensorFlow
        data_info = {
            "framework": "TensorFlow",
            "dataset": "MNIST",  # Dynamically find the dataset used in the script
            "source": "https://www.tensorflow.org/datasets/community_catalog/huggingface/mnist"
        }

    return data_info


def extract_model_details(train_file):
    # Open and parse the train.py file
    with open(train_file, "r") as f:
        script_content = f.read()

    # Search for model creation patterns (for example, PyTorch or TensorFlow models)
    model_info = {}
    hyperparameters = {}

    if "torch" in script_content:
        # Assuming PyTorch model building (can be extended for other frameworks)
        model_info = {
            "framework": "PyTorch",
            "architecture": "CNN",  # We can dynamically extract layers too if needed
        }
        hyperparameters = extract_hyperparameters(script_content)
    elif "tensorflow" in script_content:
        model_info = {
            "framework": "TensorFlow",
            "architecture": "Sequential",  # Placeholder for simplicity
        }
        hyperparameters = extract_hyperparameters(script_content)

    return model_info, hyperparameters


def extract_hyperparameters(script_content):
    # Extract hyperparameters like learning rate, batch size, etc. from the script content
    hyperparameters = {}
    if "learning_rate" in script_content:
        hyperparameters["learning_rate"] = extract_value_from_script(script_content, "learning_rate")
    if "batch_size" in script_content:
        hyperparameters["batch_size"] = extract_value_from_script(script_content, "batch_size")
    if "epochs" in script_content:
        hyperparameters["epochs"] = extract_value_from_script(script_content, "epochs")

    return hyperparameters


def extract_value_from_script(script_content, variable_name):
    # Extract a variable's value from the script content using simple parsing
    try:
        tree = ast.parse(script_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == variable_name:
                        return eval(compile(ast.Expression(node.value), filename="<ast>", mode="eval"))
    except Exception as e:
        print(f"Error extracting {variable_name}: {e}")
    return None


def get_installed_packages():
    # Collect installed packages in the environment using importlib.metadata
    installed_packages = {pkg.metadata['Name']: pkg.metadata['Version'] for pkg in importlib.metadata.distributions()}
    return installed_packages


def extract_docker_image_details(dockerfile_abs):
    # Extract Docker image information from the Dockerfile
    docker_image_info = {}
    with open(dockerfile_abs, "r") as f:
        dockerfile_content = f.read()
        if "FROM" in dockerfile_content:
            base_image = dockerfile_content.split("FROM")[1].split()[0]
            docker_image_info = {
                "name": base_image,
                "version": "latest"  # Can be more specific if needed
            }

    return docker_image_info


def get_environment_info():
    # Collect environment information like Python version and OS
    environment_info = {
        "python_version": subprocess.check_output(["python", "--version"]).strip().decode(),
        "os": subprocess.check_output(["uname", "-s"]).strip().decode() if os.name != 'nt' else "Windows"
    }

    return environment_info

if __name__ == "__main__":
    # Specify the Dockerfile path relative to the project root
    user_dockerfile = "test/Dockerfile"
    output_folder = "output"  # This folder is at the project root

    run_user_docker_container(user_dockerfile, output_folder)
    print("Process complete!")