from celery_config import celery_app
import os
import time

UPLOAD_DIR = "/app/uploads"  # Shared volume location

@celery_app.task(name="tasks.run_training", time_limit=3600)
def run_training(filename):
    """Training task"""
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)

        if not os.path.exists(file_path):
            return {"error": "File not found", "filename": filename}

        # Simulate training process
        print(f"Training started using {file_path}")



        # (Your model training logic goes here)
        time.sleep(10)

        # Delete the file after processing
        os.remove(file_path)

        return {"status": "Training completed", "filename": filename}
    except Exception as e:
        return {"error": f"An error occurred during training: {str(e)}"}
