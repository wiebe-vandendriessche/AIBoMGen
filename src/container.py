import docker

from docker.errors import BuildError, ContainerError
from docker.types import LogConfig

client = docker.from_env()

def run_user_docker_container(user_dockerfile_abs, user_dockerfile, output_folder, project_root):
    print(f"Building Docker image from {user_dockerfile_abs}...")
    try:
        image, _ = client.images.build(
            path=project_root,
            dockerfile=user_dockerfile, # relative path
            tag="user-ai-image"
        )
    except BuildError as build_error:
        print(f"Error building the Docker image: {build_error}")
        return None

    print("Starting Docker container with user's training code...")
    try:
        container = client.containers.run(
            image.id,
            name="user-ai-container",
            remove=False,
            volumes={output_folder: {'bind': '/output', 'mode': 'rw'}},
            detach=True,
            log_config=LogConfig(type="json-file"),  # Set a readable log driver
            runtime="nvidia"  # Enable GPU (requires NVIDIA runtime installed)
        )
    except ContainerError as container_error:
        print(f"Error running the Docker container: {container_error}")
        return None

    return container.id

def wait_for_container(container_id):
    container = client.containers.get(container_id)
    for log in container.logs(stream=True):
        print(log.decode(), end="")
    container.wait()
    print("Training completed.")
