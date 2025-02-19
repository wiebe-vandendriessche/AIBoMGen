import docker

client = docker.from_env()

def extract_environment_info(container):
    """
    Extract Python version and OS info from a running container by executing commands
    directly inside the container.
    """
    print("Extracting environment info from the running container...")

    # Run the `python --version` command inside the running container
    python_version_result = container.exec_run("python --version", stdout=True, stderr=True)
    python_version = python_version_result.output.decode().strip()

    # Run the `uname -a` command inside the running container to get OS info
    os_info_result = container.exec_run("uname -a", stdout=True, stderr=True)
    os_info = os_info_result.output.decode().strip()

    return {"python_version": python_version, "os": os_info}
