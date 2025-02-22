import docker

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

    command = f"inotifywait -m {mount_point} -e open -e access"
    try:
        exec_instance = container.exec_run(command, stream=True, stdout=True, stderr=True)
        for line in exec_instance.output:
            decoded_line = line.decode().strip()
            print(f"File accessed: {decoded_line}")
            log_callback(decoded_line)
    except Exception as e:
        print(f"Error monitoring file access: {e}")


def log_file_access(file_access_log, aibom):
    """
    Log file access into the AIBoM dictionary.
    """
    print(f"Logging file access: {file_access_log}")  # Add this log
    if "file_access_logs" not in aibom:
        aibom["file_access_logs"] = []
    aibom["file_access_logs"].append(file_access_log)