from celery_config import celery_app
import os
import shutil
import tensorflow as tf
import time
import stat
import yaml
import pandas as pd
import json
from aibom_generator import generate_basic_aibom, sign_aibom
from shared.minio_utils import download_file_from_minio, upload_file_to_minio
from shared.zip_utils import ZipValidationError, validate_and_extract_zip 

@celery_app.task(name="tasks.run_training", time_limit=3600)
def run_training(unique_dir, model_url, dataset_url, dataset_definition_url):
    """Training task with support for tabular and image data."""
    try:
        start_task_time = time.time()
        start_task_time_utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_task_time))
        print(f"Task started at UTC: {start_task_time_utc}")
        
        # Create a temporary directory
        temp_dir = os.path.join("/tmp", unique_dir)
        os.makedirs(temp_dir, exist_ok=True)

        # Define paths for downloaded files
        model_dir = os.path.join(temp_dir, "model")
        dataset_dir = os.path.join(temp_dir, "dataset")
        dataset_definition_dir = os.path.join(temp_dir, "definition")
        
        # Ensure directories exist
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(dataset_dir, exist_ok=True)
        os.makedirs(dataset_definition_dir, exist_ok=True)
        
        # Define filenames and paths
        model_filename = model_url.split("/")[-1]
        dataset_filename = dataset_url.split("/")[-1]
        dataset_definition_filename = dataset_definition_url.split("/")[-1]
        
        model_path = os.path.join(model_dir, model_filename)
        dataset_path = os.path.join(dataset_dir, dataset_filename)
        dataset_definition_path = os.path.join(dataset_definition_dir, dataset_definition_filename)

        # Download files from MinIO
        download_file_from_minio(f"{unique_dir}/model/{model_filename}", model_path)
        download_file_from_minio(f"{unique_dir}/dataset/{dataset_filename}", dataset_path)
        download_file_from_minio(f"{unique_dir}/definition/{dataset_definition_filename}", dataset_definition_path)

        # Load dataset definition
        with open(dataset_definition_path, "r") as f:
            dataset_definition = yaml.safe_load(f)

        # Load dataset based on type
        dataset_type = dataset_definition.get("type", "csv")
        if dataset_type == "csv":
            dataset = load_csv_dataset_with_definition(dataset_path, dataset_definition)
        elif dataset_type == "image":
            # Validate and extract the dataset .zip file
            dataset_zip_path = dataset_path
            if not os.path.exists(dataset_zip_path):
                raise FileNotFoundError(f"Dataset file {dataset_zip_path} does not exist.")
            dataset_extracted_path = os.path.join(temp_dir, "dataset_unzipped")
            os.makedirs(dataset_extracted_path, exist_ok=True)
            try:
                validate_and_extract_zip(dataset_zip_path, dataset_extracted_path)
            except ZipValidationError as e:
                raise Exception(f"Dataset validation failed: {str(e)}")
            
            dataset = load_image_dataset(dataset_extracted_path, dataset_definition)
        elif dataset_type == "tfrecord":
            dataset = load_TFRecordDataset_with_definition(dataset_path, dataset_definition)
        else:
            raise ValueError(f"Unsupported dataset type: {dataset_type}")

        # Load model
        model = tf.keras.models.load_model(model_path)

        # Validate compatibility
        validate_model_and_dataset_definition(model, dataset_definition)

        start_training_time = time.time()
        start_training_time_utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_training_time))
        print(f"Training started at UTC: {start_training_time_utc}")
        
          # Train the model
        model.fit(
            x=dataset,
            epochs=dataset_definition.get("epochs", 100),
            batch_size=dataset_definition.get("batch_size", 32),
            verbose=2
        )
        
        # Define paths for output artifacts
        trained_model_path = os.path.join(temp_dir, "trained_model.keras")
        metrics_path = os.path.join(temp_dir, "metrics.json")
        logs_path = os.path.join(temp_dir, "logs.txt")
        aibom_path = os.path.join(temp_dir, "aibom.json")
        signature_path = os.path.join(temp_dir, "aibom.sig")
 
        # Save the trained model
        model.save(trained_model_path)
        
        # Save training metrics
        with open(metrics_path, "w") as f:
            json.dump(model.history.history, f)

        # Save logs
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
        
        # Generate AIBoM
        aibom = generate_basic_aibom(input_files, output_files, config, environment)
        signature = sign_aibom(aibom, "private_key.pem")
        
        # Save AIBoM and signature
        with open(aibom_path, "w") as f:
            json.dump(aibom, f, indent=4)

        with open(signature_path, "wb") as f:  # Open in binary mode
            f.write(signature)
            
        # Upload output artifacts to MinIO
        upload_file_to_minio(trained_model_path, f"{unique_dir}/output/trained_model.keras")
        upload_file_to_minio(metrics_path, f"{unique_dir}/output/metrics.json")
        upload_file_to_minio(logs_path, f"{unique_dir}/output/logs.txt")
        upload_file_to_minio(aibom_path, f"{unique_dir}/output/aibom.json")
        upload_file_to_minio(signature_path, f"{unique_dir}/output/aibom.sig")

        result = {
            "training_status": "training job completed",
            "unique_dir": unique_dir,
            "job_id": celery_app.current_task.request.id,
            "message": "Training completed successfully and AIBoM generated.",
            "output_artifacts": [
                "trained_model.keras",
                "metrics.json",
                "logs.txt",
                "aibom.json",
                "aibom.sig",
            ],
        }
        return result    
    except Exception as e:
        # Save error logs
        error_logs_dir = os.path.join("/tmp", unique_dir)
        os.makedirs(error_logs_dir, exist_ok=True)
        error_logs_path = os.path.join(error_logs_dir, "error_logs.txt")
        with open(error_logs_path, "w") as f:
            f.write(f"An error occurred: {str(e)}\n")
        
        # Upload error logs to MinIO
        upload_file_to_minio(error_logs_path, f"{unique_dir}/error/error_logs.txt")
        
        return {
            "training_status": "training job failed",
            "unique_dir": unique_dir,
            "error": str(e)
        }
    finally:
        print(f"Task {celery_app.current_task.request.id} completed.")
                

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






def load_image_dataset(dataset_path, dataset_definition, batch_size=32):
    """
    Load and preprocess an image dataset.
    """
    # Unzip the dataset if it is a .zip file
    if dataset_path.endswith(".zip"):
        extracted_path = dataset_path.replace(".zip", "")
        shutil.unpack_archive(dataset_path, extracted_path)
        dataset_path = extracted_path

    # Load the dataset
    image_size = tuple(dataset_definition.get("image_size", [224, 224]))
    preprocessing_function = tf.keras.applications.imagenet_utils.preprocess_input

    dataset = tf.keras.preprocessing.image_dataset_from_directory(
        dataset_path,
        image_size=image_size,
        batch_size=batch_size
    )

    # Apply preprocessing if specified
    if "preprocessing" in dataset_definition:
        dataset = dataset.map(lambda x, y: (preprocessing_function(x), y))

    return dataset
                

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