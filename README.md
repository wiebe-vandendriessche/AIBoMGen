# AIBoMGen: AI Bill of Materials Generator

## Overview
AIBoMGen is a proof-of-concept tool designed to automatically generate an AI Bill of Materials (AIBoM) during the AI model training process. The tool aims to support ethical AI practices, regulatory compliance, and model traceability by tracking training dependencies, environment information, and installed packages used in AI workflows. AIBoMGen integrates Docker for containerized model training and ensures the isolation of training data within a (possible) secured environment.

## Requirements
- Docker
- Python 3.12 (3.13 does not support TensorFlow yet)

## Repository Structure

- **src/**: Contains the main Python code and logic for AIBoMGen.
   - `container.py`: Manages the lifecycle and execution of the training container.
   - `generator.py`: Handles the generation of the AI Bill of Materials.
   - `main.py`: Main entry point for running AIBoMGen.
   - **extractors/**: Responsible for extracting relevant metadata from the environment.
      - `docker_image_details.py`: Retrieves details about the Docker image used.
      - `environment_info.py`: Gathers system information such as OS version and Python version.
      - `gpu_info.py`: Extracts GPU details and usage statistics.
      - `installed_packages.py`: Lists all installed Python packages.
      - `mounted_data_access.py`: Monitors file access and add hash.
      - `__init__.py`: Marks the directory as a package.

- **test/**: Contains example training scripts and Dockerfiles.
   - `Dockerfile`: Defines the base container for training.
   - `requirements.txt`: Specifies dependencies for the training environment.
   - `train.py`: Sample AI training script uses tensorflow.
- 
- **test2/**: Another test folder uses scikit training.
   - `Dockerfile`
   - `requirements.txt`
   - `train.py`

- **test3/**: Another test folder uses tensorflow and external mounted data.
   - `Dockerfile`
   - `requirements.txt`
   - `train.py`

- **output/**: Stores generated AIBoM files and trained models.
   - Example files:
      - `aibom.json`: Generated AI Bill of Materials.
      - `model.keras`: Trained AI model output.

- **user_mounted_data/**: Contains datasets mounted by users.
   - **mnist_data/**: Example dataset.


## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
2. Start Docker Daemon
   - linux:
      ```bash
       sudo systemctl start docker
   - windows: start docker desktop
3. Make sure you defined following files in the `test/` folder:
     - `train.py` (your AI model training script)
     - `requirements.txt` (dependencies for the model)
     - `Dockerfile` (to define the container environment)
4. Run the `main.py` file in the `src/`
   ```bash
       python src/main.py

<img width="795" alt="Schermafbeelding 2025-02-23 121225" src="https://github.ugent.be/wievdndr/AIBoMGen/assets/13326/7ada3164-8b98-42bc-ba0a-af46a72d3f85">
