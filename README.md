# AIBoMGen: Hugging Face AI Bill of Materials Generator with api container starting trainer containers (versionT1)
## Overview
AIBoMGen (versionT1) is a proof-of-concept platform for training AI models using Hugging Face models and datasets. It leverages Docker to create isolated training environments and automatically generates an AI Bill of Materials (AIBoM).

## Requirements
- Docker
- Python 3.12 (3.13 does not support TensorFlow yet)

## Repository Structure

- **user/**:
    - `api.py`: API to launch trainer containers
    - `Dockerfile`: API container Dockerfile

- **trainer/**:
    - `train.py`: Training script executed inside the trainer container
    - `Dockerfile`: Trainer container Dockerfile will be built by the api container

- **dataset/**: Mounted dataset directory

- **output/**: Directory where trained models are stored

- `docker-compose.yml`: Docker Compose setup only starts the api container because trainer containers get built by api container

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
2. Start Docker Daemon
   - linux:
      ```bash
       sudo systemctl start docker
   - windows: start docker desktop
3. Build and Run the API Container
   ```bash
   docker-compose up --build

## Usage
Send a POST request to start training:
```bash
{
"dataset_path": "/dataset",
"model_name": "bert-base-uncased",
"parameters": {"epochs": 3, "learning_rate": 5e-5}
}
