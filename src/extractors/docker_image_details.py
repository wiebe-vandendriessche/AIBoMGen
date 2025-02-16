

def extract_docker_image_details(dockerfile_path):
    with open(dockerfile_path, "r") as f:
        for line in f:
            if line.startswith("FROM"):
                return {"base_image": line.split()[1]}
    return {}