from celery_config import celery_app
import os
import shutil
import tensorflow as tf
import time
import stat
import yaml
import pandas as pd
import json
from aibom_generator import generate_basic_aibom, sign_aibom, save_aibom

UPLOAD_DIR = "/app/uploads"  # Shared volume location

@celery_app.task(name="tasks.run_training", time_limit=3600)
def run_training(model_filename, dataset_filename, dataset_definition_filename, unique_dir):
    """Training task"""
    try:
        start_task_time = time.time()
        start_task_time_utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_task_time))
        print(f"Task started at UTC: {start_task_time_utc}")
        
        model_path = os.path.join(unique_dir, model_filename)
        dataset_path = os.path.join(unique_dir, dataset_filename)
        dataset_definition_path = os.path.join(unique_dir, dataset_definition_filename)

        # Ensure files exist
        if not os.path.exists(model_path):
            return {"error": "Model file not found", "model": model_path}
        if not os.path.exists(dataset_path):
            return {"error": "Dataset file not found", "dataset": dataset_path}
        if not os.path.exists(dataset_definition_path):
            return {"error": "Dataset definition file not found", "dataset_definition": dataset_definition_path}

        # Load dataset definition
        with open(dataset_definition_path, "r") as f:
            dataset_definition = yaml.safe_load(f)

        # Load dataset
        dataset = load_csv_dataset_with_definition(dataset_path, dataset_definition)

        # Load model
        model = tf.keras.models.load_model(model_path)

        # Validate compatibility
        validate_model_and_dataset_definition(model, dataset_definition)

        start_training_time = time.time()
        start_training_time_utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_training_time))
        print(f"Training started at UTC: {start_training_time_utc}")
        
        # Train the model
        model.fit(x=dataset, epochs=100, batch_size=32, verbose=2)
        
        # Save the trained model
        trained_model_path = os.path.join(unique_dir, "trained_model.keras")
        model.save(trained_model_path)
        
        # Save training metrics
        metrics_path = os.path.join(unique_dir, "metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(model.history.history, f)  # Use model.history.history instead of model.history
        # Save logs
        logs_path = os.path.join(unique_dir, "logs.txt")
        with open(logs_path, "w") as f:
            f.write("Training completed successfully.\n")
            
        start_aibom_time = time.time()
        start_aibom_time_utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_aibom_time))
        print(f"AIBoM generation started at UTC: {start_aibom_time_utc}")
        
        # Generate and save the AIBoM
        input_files = [model_path, dataset_path, dataset_definition_path]
        output_files = [trained_model_path, metrics_path, logs_path]
        config = {"epochs": 100, "batch_size": 32}
        
        # Set capture environment
        environment = {
            "python_version": "3.9",
            "tensorflow_version": tf.__version__,
            "request_time": start_task_time_utc,
            "start_training_time": start_training_time_utc,
            "start_aibom_time": start_aibom_time_utc,
            "training_time": start_aibom_time - start_training_time,
            "job_id": celery_app.current_task.request.id,
            "unique_dir": unique_dir,
        }
        
        aibom = generate_basic_aibom(input_files, output_files, config, environment)
        signature = sign_aibom(aibom, "private_key.pem")
        save_aibom(aibom, signature, unique_dir)

        result = {
            "training_status": "training job completed",
            "unique_dir": unique_dir,
            "job_id": celery_app.current_task.request.id,
            "message": "Training completed successfully and AIBoM generated.",
            "aibom_path": os.path.join(unique_dir, "aibom.json"),
            "signature_path": os.path.join(unique_dir, "aibom.sig"),
            "trained_model_path": trained_model_path,
        }
        return result    
    except Exception as e:
        # Save error logs
        error_logs_path = os.path.join(unique_dir, "error_logs.txt")
        with open(error_logs_path, "w") as f:
            f.write(f"An error occurred: {str(e)}\n")
        return {
            "training_status": "training job failed",
            "unique_dir": unique_dir,
            "error": str(e)
        }
    finally:
        print("Task ${run_training.request.id} completed.")
        print("Data in the unique directory:")
        for filename in os.listdir(unique_dir):
            print(f"- {filename}")
                

        # model.fit(
        #     x=None, # data (could be: numpy array, tensor, dict mapping, tf.data.Dataset, keras.utils.PyDataset)
        #     y=None, # label (could be: numpy array, (if x is dataset,generator or pydataset, y should not be specified))
        #     batch_size=None, # Number of samples per gradient update, default 32 (if x is dataset,generator or pydataset, batch_size should not be specified)
        #     epochs=1, # Number of epochs to train
        #     verbose='auto', # 0: silent, 1: progress bar, 2: one line per epoch (when writing to file)
        #     callbacks=None, # (tensorboard)
        #     validation_split=0.0, # Fraction of train data used to validate (if x is dataset,generator or pydataset, validation_split should not be specified)
        #     validation_data=None, # data to val (could be: numpy array, tensor, dict mapping, tf.data.Dataset, keras.utils.PyDataset)
        #     shuffle=True, # shuffle x after each epoch (if x is dataset,generator or pydataset, shuffle should not be specified)
        #     class_weight=None, # Optional dictionary mapping class indices (integers) to a weight (float) value, used for weighting the loss function (during training only). This can be useful to tell the model to "pay more attention" to samples from an under-represented class.
        #     sample_weight=None, # Optional NumPy array of weights for the training samples, used for weighting the loss function (during training only). Y
        #     initial_epoch=0, # Epoch at which to start training (useful for resuming a previous training run).
        #     steps_per_epoch=None, # Total number of steps (batches of samples) before declaring one epoch finished and starting the next epoch. Epoch at which to start training (useful for resuming a previous training run).
        #     validation_steps=None, # Only relevant if validation_data is provided. Total number of steps (batches of samples) to draw before stopping when performing validation at the end of every epoch.
        #     validation_batch_size=None, # Number of samples per validation batch.
        #     validation_freq=1 # Specifies how many training epochs to run before a new validation run is performed
        # )




def load_csv_dataset_with_definition(file_path, dataset_definition, batch_size=32):
    """
    Load and preprocess a CSV dataset based on the dataset definition.
    """
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Validate that all required columns are present
    required_columns = list(dataset_definition["columns"].keys())
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"CSV file is missing required columns: {set(required_columns) - set(df.columns)}")

    # Extract features and labels
    feature_columns = [col for col in dataset_definition["columns"].keys() if col != dataset_definition["label"]]
    label_column = dataset_definition["label"]

    features = df[feature_columns].astype("float32").values
    labels = df[label_column].astype("int64").values

    # Apply preprocessing if specified
    if "preprocessing" in dataset_definition:
        features = apply_preprocessing(features, dataset_definition["preprocessing"])

    # Convert to TensorFlow Dataset
    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    return dataset.batch(batch_size).shuffle(buffer_size=1000)
















                

def load_tfrecord_demo(file_path, batch_size=32):
    """Helper function to load a TFRecord file and return a tf.data.Dataset."""
    raw_dataset = tf.data.TFRecordDataset(file_path)

    # Define the feature description to match the TFRecord dataset generated above
    feature_description = {
        'feature': tf.io.FixedLenFeature([10], tf.float32),  # 10 features (10 float values)
        'label': tf.io.FixedLenFeature([1], tf.int64),  # 1 label (binary classification)
    }

    def _parse_function(proto):
        # Parse the input tf.Example proto using the feature description
        parsed_features = tf.io.parse_single_example(proto, feature_description)
        return parsed_features['feature'], parsed_features['label']  # Return feature and label

    # Parse the TFRecord file and create a dataset
    dataset = raw_dataset.map(_parse_function)

    # Batch the dataset and shuffle it for training
    dataset = dataset.batch(batch_size).shuffle(buffer_size=1000)

    return dataset

def load_TFRecordDataset_with_definition(file_path, dataset_definition, batch_size=32):
    """
    Load and preprocess the dataset based on the dataset definition.
    Dynamically handles feature shapes and preprocessing steps.
    """
    raw_dataset = tf.data.TFRecordDataset(file_path)

    # Build feature description from dataset definition
    feature_description = {
        feature: tf.io.FixedLenFeature(
            shape if isinstance(shape, list) else [],  # Handle scalar or vector features
            tf.float32 if dtype == "float" else tf.int64
        )
        for feature, (dtype, shape) in dataset_definition["features"].items()
    }
    feature_description[dataset_definition["label"]] = tf.io.FixedLenFeature([], tf.int64)

    def _parse_function(proto):
        # Parse the input tf.Example proto using the feature description
        parsed_features = tf.io.parse_single_example(proto, feature_description)

        # Extract features as a flat tensor or dictionary based on the definition
        if dataset_definition.get("flatten_features", True):
            features = tf.concat(
                [tf.reshape(parsed_features[k], [-1]) for k in dataset_definition["features"].keys()],
                axis=-1
            )
        else:
            features = {k: parsed_features[k] for k in dataset_definition["features"].keys()}

        label = parsed_features[dataset_definition["label"]]

        # Apply optional preprocessing if specified
        if "preprocessing" in dataset_definition:
            features = apply_preprocessing(features, dataset_definition["preprocessing"])

        return features, label

    dataset = raw_dataset.map(_parse_function)
    return dataset.batch(batch_size).shuffle(buffer_size=1000)

def validate_model_and_dataset_definition(model, dataset_definition):
    """Validate that the model's input/output shapes match the dataset definition."""
    input_shape = model.input_shape[1:]  # Exclude batch dimension
    output_shape = model.output_shape[1:]  # Exclude batch dimension

    if input_shape != tuple(dataset_definition["input_shape"]):
        raise ValueError(f"Model input shape {input_shape} does not match dataset input shape {dataset_definition['input_shape']}")

    if output_shape != tuple(dataset_definition["output_shape"]):
        raise ValueError(f"Model output shape {output_shape} does not match dataset output shape {dataset_definition['output_shape']}")
    
def apply_preprocessing(features, preprocessing_steps):
    """
    Apply preprocessing steps to the features.
    Supports normalization, scaling, and other transformations.
    """
    if preprocessing_steps.get("normalize", False):
        features = tf.math.l2_normalize(features, axis=-1)

    if "scale" in preprocessing_steps:
        scale = preprocessing_steps["scale"]
        features = features * scale

    if "clip" in preprocessing_steps:
        min_val, max_val = preprocessing_steps["clip"]
        features = tf.clip_by_value(features, min_val, max_val)

    return features