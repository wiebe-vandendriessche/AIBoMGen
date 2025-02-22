import docker
import hashlib
import time
import os
import threading

client = docker.from_env()


def is_inotify_installed(container):
    """Check if inotify-tools is installed in the container."""
    try:
        exec_result = container.exec_run("which inotifywait")
        return exec_result.exit_code == 0
    except Exception as e:
        print(f"Error checking for inotify: {e}")
        return False

def monitor_file_access_in_container(container, mount_point, log_callback):
    """Monitor file accesses in the container only if inotify-tools is available."""
    if not is_inotify_installed(container):
        print("Skipping file access monitoring: inotify-tools not found in container.")
        return

    # Exclude accesses caused by sha256sum to avoid infinite recursion
    command = f"inotifywait -m {mount_point} -e open -e access"
    try:
        exec_instance = container.exec_run(command, stream=True, stdout=True, stderr=True)
        for line in exec_instance.output:
            decoded_line = line.decode().strip()
            print(f"File accessed: {decoded_line}")
            log_callback(decoded_line)
    except Exception as e:
        print(f"Error monitoring file access: {e}")

def compute_file_hash_on_host(file_path):
    """
    Compute the SHA-256 hash of a file's contents on the host system.
    """
    try:
        with open(file_path, "rb") as file:
            sha256_hash = hashlib.sha256()
            # Read the file in chunks to avoid large memory usage
            for byte_block in iter(lambda: file.read(4096), b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error: Failed to compute hash for {file_path} on the host system. {e}")
        return None

def file_exists_in_container(container, file_path):
    """Check if a file exists inside the container."""
    exec_result = container.exec_run(f"ls {file_path}")
    return exec_result.exit_code == 0  # If the file exists, the exit code will be 0

def log_file_access(file_access_log, aibom, mount_point, container, mounted_data_abs):
    """
    Log file access into the AIBoM dictionary along with the file hash.
    """
    print(f"Logging file access: {file_access_log}")

    # Extracting the file name from the log entry
    try:
        file_name = file_access_log.split()[-1]  # Assuming the file name is the last item
    except IndexError:
        print("Error: Unable to extract file name from log entry.")
        return

    # Constructing the full file path on the host system (using the mount point and the file name)
    full_file_path = os.path.join(mounted_data_abs, file_name)  # This should point to the host machine's path

    # Normalize file path to use forward slashes
    full_file_path = full_file_path.replace("\\", "/")

    # Now we calculate the hash on the host machine
    print(f"Hashing file: {file_access_log}")
    file_hash = compute_file_hash_on_host(full_file_path)

    if file_hash:
        if "file_access_logs" not in aibom:
            aibom["file_access_logs"] = []
        aibom["file_access_logs"].append({"file": full_file_path, "hash": file_hash})
    else:
        print(f"Failed to compute hash for file: {full_file_path}")