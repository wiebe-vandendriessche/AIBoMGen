import os

import container
import generator

def main():

    user_dockerfile = "test/Dockerfile"
    output_folder = "output"
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Construct the absolute path to the Dockerfile
    user_dockerfile_abs = os.path.join(project_root, user_dockerfile)
    output_folder_abs = os.path.join(project_root, output_folder)

    container_id = container.run_user_docker_container(user_dockerfile_abs, user_dockerfile, output_folder_abs, project_root)
    print("Waiting for training to complete...")
    container.wait_for_container(container_id)

    print("Generating AIBoM...")
    generator.generate_aibom(user_dockerfile_abs, output_folder_abs, project_root, container_id)
    print("AIBoM complete...")

    print("Process complete!")

if __name__ == "__main__":
    main()