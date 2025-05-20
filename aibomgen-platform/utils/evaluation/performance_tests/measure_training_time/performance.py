import os
import requests
import csv

# This script only works if the platform is running without authentication


# === Configuration ===
API_URL = "http://localhost:8000/developer/submit_job_by_model_and_data"

DOWNLOADS_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")

MODEL_FILE = os.path.join(DOWNLOADS_FOLDER, "cifar10_model.keras")
DATASET_FILE = os.path.join(DOWNLOADS_FOLDER, "cifar10_dataset.zip")
DATASET_DEF_FILE = os.path.join(DOWNLOADS_FOLDER, "cifar10_definition.yaml")

# The last epoch will not succeed on purpose, as it is used to test the slowapi timeout (dissable slowapi if you want it to succeed)

epochs_list = [1, 3, 5, 10, 20, 50]

# === Submit jobs ===
for epochs in epochs_list:
    with open(MODEL_FILE, "rb") as model_f, \
            open(DATASET_FILE, "rb") as dataset_f, \
            open(DATASET_DEF_FILE, "rb") as def_f:

        files = {
            "model": model_f,
            "dataset": dataset_f,
            "dataset_definition": def_f,
        }
        data = {
            "framework": "TensorFlow 2.16.1",
            "model_name": "cifar_cnn",
            "epochs": epochs,
            # Add other fields as needed
        }

        response = requests.post(API_URL, files=files, data=data)
        print(
            f"Epochs: {epochs} | Status: {response.status_code} | Response: {response.text}")

# WARNING: Running multiple training jobs in parallel on the 3 workers of the platform when deployed
# on a single machine may cause the machine to run out of memory and crash.
# This is because the platform is not designed to handle multiple training jobs in parallel on a single machine.

# Minimum requirements that should be ok when running the platform on a single machine:
# - 32 GB RAM (assign enough RAM to each worker)
# - 8 CPU cores (assign enough CPU cores to each worker)
# - 1 GPU (i have RTX 3060)

# If all jobs are completed successfully (use flower dashboard localhost:5555)
# you can retrieve the aibom or logs and look at the timestamps
