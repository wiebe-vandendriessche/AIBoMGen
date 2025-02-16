import docker

client = docker.from_env()

def extract_environment_info(container):
    """
    Extract Python version and OS info from a stopped container
    by running a temporary container.
    """
    image_id = container.image.id  # Get the image of the stopped container

    print("Extracting environment info using a temporary container...")

    # Run a temporary container to get Python version
    python_version = client.containers.run(
        image=image_id,
        command="python --version",
        remove=True,
        detach=False,
        stdout=True
    ).decode().strip()

    # Run another temporary container to get OS info
    os_info = client.containers.run(
        image=image_id,
        command="uname -a",
        remove=True,
        detach=False,
        stdout=True
    ).decode().strip()

    return {"python_version": python_version, "os": os_info}
