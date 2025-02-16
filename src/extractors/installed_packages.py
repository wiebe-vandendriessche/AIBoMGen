import importlib.metadata

def get_installed_packages():
    # Collect installed packages in the environment using importlib.metadata
    installed_packages = {pkg.metadata['Name']: pkg.metadata['Version'] for pkg in importlib.metadata.distributions()}
    return installed_packages