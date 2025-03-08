import docker
from fastapi import APIRouter, HTTPException
from docker.errors import APIError
import uuid
from typing import Optional
from pydantic import BaseModel

router = APIRouter()
docker_client = docker.from_env()

TRAINER_DOCKERFILE_PATH = "/trainer"
TRAINER_IMAGE = "aibomgen_trainer"  # Name of the trainer image
NETWORK_NAME = "aibomgen_network"  # Correct network name


# Pydantic model to define the API request body
class TrainingRequest(BaseModel):
    dataset_path: str  # Path to the dataset (can be a directory or specific file)
    model_name: str  # Model name (e.g., "bert-base-uncased")
    parameters: dict  # Dictionary to hold hyperparameters (e.g., {'learning_rate': 0.01, 'epochs': 3})

def image_exists(image_name):
    """Check if a Docker image exists"""
    try:
        images = docker_client.images.list(name=image_name)
        return len(images) > 0
    except docker.errors.APIError as e:
        return False

@router.post("/start-training")
async def start_training(request: TrainingRequest):
    """Starts a new training container with the provided request data."""
    try:
        # Ensure the image exists, or build it
        # if not image_exists(TRAINER_IMAGE):
        #    print(f"Building image {TRAINER_IMAGE}...")
        #    docker_client.images.build(path=TRAINER_DOCKERFILE_PATH, tag=TRAINER_IMAGE)

        # always build it
        docker_client.images.build(path=TRAINER_DOCKERFILE_PATH, tag=TRAINER_IMAGE)

        # Create or get the network
        network_name = NETWORK_NAME

        # Map dataset directories from the request
        volumes = {
            request.dataset_path: {'bind': '/dataset', 'mode': 'ro'},  # Mount the dataset path to /dataset inside the container
            '/output/trained_model': {'bind': '/mnt/trained_model', 'mode': 'rw'}  # Mount model save path
        }

        # Start the trainer container and attach to the network, mount the dataset
        container = docker_client.containers.run(
            TRAINER_IMAGE,
            detach=True,
            remove=False,  # Remove container after it stops
            name=f"trainer_{container_id()}",
            network=network_name,  # Attach the container to the network
            volumes=volumes,  # Mount the dataset volumes to the container
            environment={
                "MODEL_NAME": request.model_name,  # Set the model name as an environment variable
                "DATASET_PATH": "/dataset",  # Path to the dataset inside the container
                **request.parameters  # Pass hyperparameters as environment variables
            }
        )

        return {"message": "Training container started!", "container_id": container.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def container_id():
    """Generates a short unique ID for the container"""
    return str(uuid.uuid4())[:8]