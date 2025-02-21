import os
import container
import generator

def main():
    user_dockerfile = "test3/Dockerfile"
    output_folder = "output"
    mounted_data = "user_mounted_data/mnist_data"
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Construct the absolute path to the Dockerfile
    user_dockerfile_abs = os.path.join(project_root, user_dockerfile)
    output_folder_abs = os.path.join(project_root, output_folder)

    mounted_data_abs = os.path.join(project_root, mounted_data)

    container_id = container.run_user_docker_container(user_dockerfile_abs, user_dockerfile, output_folder_abs, mounted_data_abs, project_root)
    print("Container started, collecting environment and package information...")

    # Part 1: Extract environment and installed packages as soon as the container is running
    generator.collect_initial_aibom_data(user_dockerfile_abs, output_folder_abs, project_root, container_id)

    print("Waiting for training to complete...")
    container.wait_for_container(container_id)

    print("Training completed, generating AIBoM...")
    # Part 2: Extract final training data and generate AIBoM after training completes
    generator.generate_aibom_after_training(user_dockerfile_abs, output_folder_abs, project_root, container_id)

    print("Process complete!")

if __name__ == "__main__":
    main()
