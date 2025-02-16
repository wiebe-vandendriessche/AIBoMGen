

def extract_docker_image_details(dockerfile_abs):
    # Extract Docker image information from the Dockerfile
    docker_image_info = {}
    with open(dockerfile_abs, "r") as f:
        dockerfile_content = f.read()
        if "FROM" in dockerfile_content:
            base_image = dockerfile_content.split("FROM")[1].split()[0]
            docker_image_info = {
                "name": base_image,
                "version": "latest"  # Can be more specific if needed
            }

    return docker_image_info