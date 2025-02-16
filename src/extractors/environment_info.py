import os
import subprocess

def get_environment_info():
    # Collect environment information like Python version and OS
    environment_info = {
        "python_version": subprocess.check_output(["python", "--version"]).strip().decode(),
        "os": subprocess.check_output(["uname", "-s"]).strip().decode() if os.name != 'nt' else "Windows"
    }
    return environment_info