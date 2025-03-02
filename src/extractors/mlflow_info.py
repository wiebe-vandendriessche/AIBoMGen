import mlflow
import docker
from mlflow.tracking import MlflowClient
import os

def get_model_summary_from_artifact(run_id):
    client = MlflowClient(tracking_uri="file:///output/mlruns")

    try:
        # List artifacts for the given run
        artifacts = client.list_artifacts(run_id)
        # Find the model_summary.txt artifact
        model_summary_artifact = next((artifact for artifact in artifacts if artifact.path == "model_summary.txt"), None)

        if model_summary_artifact:
            # Download the artifact content into memory
            artifact_path = client.download_artifacts(run_id, model_summary_artifact.path)

            # Open the downloaded file and read its content
            with open(artifact_path, "rb") as file:
                content = file.read()

            # Try decoding the content into text
            try:
                text_content = content.decode("utf-8")
                return text_content
            except UnicodeDecodeError:
                return "The content of the model summary artifact is not valid UTF-8 text."

    except Exception as e:
        return f"Error retrieving model summary artifact: {str(e)}"


def extract_mlflow_info(aibom, output_folder):
    client = MlflowClient(tracking_uri="file:///output/mlruns")
    try:
        experiment = client.get_experiment_by_name("my_experiment")
        if not experiment:
            aibom["mlflow_info"] = "No MLflow experiment found"
            return

        runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time desc"], max_results=1)
        if not runs:
            aibom["mlflow_info"] = "No MLflow runs found"
            return

        run = runs[0]

        artifacts = [str(artifact) for artifact in client.list_artifacts(run.info.run_id)] if client.list_artifacts(run.info.run_id) else []

        # Get the model summary content
        model_summary = get_model_summary_from_artifact(run.info.run_id)

        aibom["mlflow_info"] = {
            "experiment_id": experiment.experiment_id,
            "experiment_name": experiment.name,
            "run_id": run.info.run_id,
            "run_start_time": run.info.start_time,
            "run_end_time": run.info.end_time,
            "status": run.info.status,
            "parameters": run.data.params,
            "metrics": run.data.metrics,
            "tags": run.data.tags,
            "artifacts": artifacts,
            "model_summary": model_summary  # Include the content of the model summary
        }
    except Exception as e:
        aibom["mlflow_info"] = f"Error extracting MLflow info: {str(e)}"

    print(aibom["mlflow_info"])