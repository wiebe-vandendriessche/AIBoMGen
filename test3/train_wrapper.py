import os
import mlflow

# Set the output folder where the logs will be stored
output_folder = "/output"  # Make sure this path matches your Docker volume mapping


# Set MLflow's tracking URI to use the /output directory for artifacts
mlflow.set_tracking_uri(f"file://{output_folder}/mlruns")

mlflow.set_experiment("my_experiment")  # Use your desired experiment name

# Start MLflow run
mlflow.start_run()

# Enable TensorFlow autologging or other framework autologging if needed
mlflow.tensorflow.autolog()  # Replace with the relevant autologging method for your framework

print("Current Tracking URI:", mlflow.get_tracking_uri())
# Print the current run ID
current_run_id = mlflow.active_run().info.run_id
current_experiment = mlflow.get_experiment_by_name("my_experiment")
print("Current Run ID:", current_run_id)
print(current_experiment)

# Run train.py code in the same process
train_file = "train.py"  # Provide the correct path to train.py

with open(train_file) as f:
    code = f.read()
    exec(code)  # Executes the code from train.py in the same process

# End MLflow run
mlflow.end_run()