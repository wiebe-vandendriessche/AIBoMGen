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
    dataset_path: str  # Path to the dataset (directory containing training data)
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
        # # Check if the trainer image exists
        # if not image_exists(TRAINER_IMAGE):
        #     # Build the image if it doesn't exist
        #     docker_client.images.build(path=TRAINER_DOCKERFILE_PATH, tag=TRAINER_IMAGE)

        docker_client.images.build(path=TRAINER_DOCKERFILE_PATH, tag=TRAINER_IMAGE)

        # Generate a unique container name
        container_name = f"trainer_{container_id()}"

        # Define volumes for dataset mounting and model saving
        volumes = {
            '/dataset/imdb': {'bind': '/mnt/dataset/imdb', 'mode': 'ro'},  # Mount dataset to a different path
            '/output/trained_model': {'bind': '/mnt/trained_model', 'mode': 'rw'},  # Mount output directory
        }

        # Start the training container
        container = docker_client.containers.run(
            TRAINER_IMAGE,
            detach=True,
            remove=False,  # Do not remove immediately, allow logs to be inspected
            name=container_name,
            network=NETWORK_NAME,  # Attach container to the network
            volumes=volumes,  # Mount dataset and output directories
            environment={
                "MODEL_NAME": request.model_name,  # Hugging Face model name
                "DATASET_PATH": '/mnt/dataset/imdb',  # Path to dataset inside container
                **request.parameters  # Hyperparameters as environment variables
            }
        )

        return {"message": "Training container started!", "container_id": container.id}
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Docker API Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")

def container_id():
    """Generates a short unique ID for the container"""
    return str(uuid.uuid4())[:8]

