import subprocess

def run_user_docker_container(dockerfile_path, output_folder, project_root):

    print(f"Building Docker image from {dockerfile_path}...")
    # Build the Docker image using the project root as the build context
    subprocess.run(
        ["docker", "build", "-t", "user-ai-image", "-f", dockerfile_path, "."],
        cwd=project_root
    )

    # Run the Docker container and mount the output folder
    print("Starting Docker container with user's training code...")
    subprocess.Popen(
        ["docker", "run", "--rm", "-v", f"{output_folder}:/output", "user-ai-image"],
        cwd=project_root
    )
