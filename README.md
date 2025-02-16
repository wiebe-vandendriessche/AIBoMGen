# AIBoMGen: AI Bill of Materials Generator

## Overview
AIBoMGen is a proof-of-concept tool designed to automatically generate an AI Bill of Materials (AIBoM) during the AI model training process. The tool aims to support ethical AI practices, regulatory compliance, and model traceability by tracking training dependencies, environment information, and installed packages used in AI workflows. AIBoMGen integrates Docker for containerized model training and ensures the isolation of training data within a (possible) secured environment.

## Requirements
- Docker
- Python 3.12 (3.13 does not support TensorFlow yet)
- Dependencies you list in `requirements.txt` for your own model to train

## Repository Structure

- **src/**: Contains the main Python code and logic for AIBoMGen.
- **test/**: Includes example training scripts and Dockerfiles for image generation to test.
- **test/Dockerfile**: Defines the base image and setup for the Docker container used for model training.
- **test/requirements.txt**: Lists all Python dependencies required for the project.
- **output/**: Directory where generated AIBoM and model artifacts are saved.

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
2. Start Docker Daemon
   ```bash
    sudo systemctl start docker
3. Make sure you defined following files in the `test/` folder:
     - `train.py` file (for your AI model)
     - `requirements.txt` file
     - `Dockerfile`
4. Run the `main.py` file in the `src/`