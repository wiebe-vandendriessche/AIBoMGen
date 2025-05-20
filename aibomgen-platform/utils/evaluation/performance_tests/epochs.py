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


# Epochs: 1 | Status: 200 | Response: {"job_id":"0896113c-2c84-4e92-9478-688d620e5c9f","status":"Training started","unique_dir":"00c383d1-b478-49d6-bc4e-c3458ba1122d"}
# Epochs: 3 | Status: 200 | Response: {"job_id":"a601f929-daef-43e3-8887-2ff0ef194c49","status":"Training started","unique_dir":"37508286-5c53-4537-8212-8c21b9cbc768"}
# Epochs: 5 | Status: 200 | Response: {"job_id":"7a5e2599-0e39-4e1b-8945-bbc0baa4b5b5","status":"Training started","unique_dir":"d67ee302-7315-4b7e-9747-f8abd1ec48a7"}
# Epochs: 10 | Status: 200 | Response: {"job_id":"4da0437f-fb84-4652-a749-57b4ed7bf0af","status":"Training started","unique_dir":"e65b44b3-d83c-46dd-989e-cdfa823b1eb5"}
# Epochs: 20 | Status: 200 | Response: {"job_id":"db6870f6-7308-4382-89c7-a32c91a1c429","status":"Training started","unique_dir":"df490a48-9cec-4fdd-8ff8-da420014c8d4"}
# Epochs: 50 | Status: 429 | Response: {"detail":"5 per 1 minute"}
