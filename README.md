# AIBoMGen: Hugging Face Training API with AIBoM gen

## Overview
This project provides an API for training AI models using Hugging Face datasets with integrity verification. The training runs in a Celery worker and ensures dataset integrity by hashing the dataset before training.

## Requirements
- Docker
- Python 3.12 (3.13 does not support TensorFlow yet)

## Repository Structure
- **api/**: 
   - `Dockerfile`:
   - `requirements.txt`: 
   - `app.py`:
- **worker/**: Another test folder uses scikit training.
   - `Dockerfile`
   - `requirements.txt`
   - `tasks.py`
   - `celery_config.py`
- `docker-compose.yml`

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd aibomgen
2. Start Docker Daemon
   - linux:
      ```bash
       sudo systemctl start docker
   - windows: start docker desktop
3. Start Docker Compose:
   ```bash
   docker-compose up --build

## Usage
- The FastAPI service runs on http://localhost:8000
- Submit a training job using the API
  - POST `/submit_job`
  - Request body:
  ```json
    {
    "model_name": "distilbert-base-uncased",
    "dataset_name": "imdb"
    }
- Monitor job status and retrieve results
