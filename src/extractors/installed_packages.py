import docker

client = docker.from_env()

def extract_installed_packages(container):
    """
    Extract installed Python packages from a stopped container by creating
    a temporary container from the same image and running `pip freeze`.
    """
    image_id = container.image.id  # Get the image from the stopped container

    print("Extracting installed packages using a temporary container...")

    # Run a new temporary container just for package extraction
    temp_container = client.containers.run(
        image=image_id,
        command="pip freeze",
        remove=True,
        detach=False,  # Run in foreground to capture output
        stdout=True
    )

    # Decode the output and parse installed packages
    packages = temp_container.decode().splitlines()
    return {pkg.split("==")[0]: pkg.split("==")[1] for pkg in packages if "==" in pkg}
