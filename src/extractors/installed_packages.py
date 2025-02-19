import docker

client = docker.from_env()

def extract_installed_packages(container):
    """
    Extract installed Python packages from a running container by executing
    `pip freeze` inside the container.
    """
    print("Extracting installed packages from the running container...")

    # Run the `pip freeze` command inside the running container
    result = container.exec_run("pip freeze", stdout=True, stderr=True)

    # Decode the output and parse installed packages
    packages = result.output.decode().splitlines()
    return {pkg.split("==")[0]: pkg.split("==")[1] for pkg in packages if "==" in pkg}
