import tensorflow as tf
import pandas as pd
import yaml
import json
from shared.zip_utils import ZipValidationError, validate_and_extract_zip
import numpy as np


def load_csv_dataset_with_definition(task_logger, file_path, dataset_definition, batch_size=32):
    """
    Load and preprocess a CSV dataset based on the dataset definition.
    """
    task_logger.info(f"Loading CSV dataset from: {file_path}")

    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)
    task_logger.info(
        f"CSV file loaded successfully. Number of rows: {len(df)}")

    # Validate that all required columns are present
    required_columns = list(dataset_definition["columns"].keys())
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        task_logger.error(
            f"CSV file is missing required columns: {missing_columns}")
        raise ValueError(
            f"CSV file is missing required columns: {missing_columns}")
    task_logger.info("All required columns are present in the CSV file.")

    # Extract features and labels
    feature_columns = [col for col in dataset_definition["columns"].keys()
                       if col != dataset_definition["label"]]
    label_column = dataset_definition["label"]
    task_logger.info(f"Feature columns: {feature_columns}")
    task_logger.info(f"Label column: {label_column}")

    features = df[feature_columns].astype("float32").values
    labels = df[label_column].astype("int64").values
    task_logger.info(
        f"Extracted features and labels. Number of features: {len(features[0])}, Number of labels: {len(labels)}")

    # Map labels to 0-based indices if not already 0-based
    unique_labels = sorted(set(labels))
    if min(unique_labels) != 0 or max(unique_labels) != len(unique_labels) - 1:
        label_map = {v: i for i, v in enumerate(unique_labels)}
        labels = np.array([label_map[val] for val in labels])
        task_logger.info(f"Mapped labels to 0-based indices: {label_map}")

    # Apply preprocessing if specified
    if "preprocessing" in dataset_definition:
        task_logger.info("Applying preprocessing steps to features.")
        features = apply_preprocessing(
            features, dataset_definition["preprocessing"], task_logger)
        task_logger.info("Preprocessing completed.")

    # Convert to TensorFlow Dataset
    task_logger.info("Converting data to TensorFlow Dataset.")
    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    dataset = dataset.batch(batch_size).shuffle(buffer_size=1000)
    task_logger.info(
        f"Dataset created successfully with batch size: {batch_size}")

    return dataset


def load_image_dataset(task_logger, dataset_path, dataset_definition, batch_size=32):
    """
    Load and preprocess an image dataset.
    """
    task_logger.info(f"Loading image dataset from: {dataset_path}")

    # Load the dataset
    image_size = tuple(dataset_definition.get("image_size", [224, 224]))
    task_logger.info(f"Using image size: {image_size}")
    preprocessing_function = tf.keras.applications.imagenet_utils.preprocess_input

    try:
        task_logger.info("Loading images from directory...")
        dataset = tf.keras.preprocessing.image_dataset_from_directory(
            dataset_path,
            image_size=image_size,
            batch_size=batch_size
        )
        task_logger.info("Image dataset loaded successfully.")
    except Exception as e:
        task_logger.error(f"Failed to load image dataset: {str(e)}")
        raise

    # Apply preprocessing if specified
    if "preprocessing" in dataset_definition:
        task_logger.info("Applying preprocessing steps to the dataset.")
        try:
            dataset = dataset.map(lambda x, y: (preprocessing_function(x), y))
            task_logger.info("Preprocessing applied successfully.")
        except Exception as e:
            task_logger.error(f"Failed to apply preprocessing: {str(e)}")
            raise
    else:
        task_logger.info(
            "No preprocessing steps specified in the dataset definition.")

    task_logger.info(
        f"Dataset creation completed with batch size: {batch_size}")
    return dataset


def load_tfrecord_demo(file_path, batch_size=32):
    """Helper function to load a TFRecord file and return a tf.data.Dataset."""
    raw_dataset = tf.data.TFRecordDataset(file_path)

    # Define the feature description to match the TFRecord dataset generated above
    feature_description = {
        # 10 features (10 float values)
        'feature': tf.io.FixedLenFeature([10], tf.float32),
        # 1 label (binary classification)
        'label': tf.io.FixedLenFeature([1], tf.int64),
    }

    def _parse_function(proto):
        # Parse the input tf.Example proto using the feature description
        parsed_features = tf.io.parse_single_example(
            proto, feature_description)
        # Return feature and label
        return parsed_features['feature'], parsed_features['label']

    # Parse the TFRecord file and create a dataset
    dataset = raw_dataset.map(_parse_function)

    # Batch the dataset and shuffle it for training
    dataset = dataset.batch(batch_size).shuffle(buffer_size=1000)

    return dataset


def load_TFRecordDataset_with_definition(task_logger, file_path, dataset_definition, batch_size=32):
    """
    Load and preprocess the dataset based on the dataset definition.
    Dynamically handles feature shapes and preprocessing steps.
    """
    raw_dataset = tf.data.TFRecordDataset(file_path)

    # Build feature description from dataset definition
    feature_description = {}
    for feature, info in dataset_definition["features"].items():
        dtype = info.get("dtype", "float32")
        shape = info.get("shape", [])
        tf_dtype = tf.float32 if dtype in ["float", "float32"] else tf.int64
        feature_description[feature] = tf.io.FixedLenFeature(shape, tf_dtype)

    label_name = dataset_definition["label"]["name"]
    label_dtype = dataset_definition["label"].get("dtype", "int64")
    feature_description[label_name] = tf.io.FixedLenFeature(
        [], tf.int64 if label_dtype == "int64" else tf.float32)

    def _parse_function(proto):
        # Parse the input tf.Example proto using the feature description
        parsed_features = tf.io.parse_single_example(
            proto, feature_description)

        # Extract features as a flat tensor or dictionary based on the definition
        if dataset_definition.get("flatten_features", True):
            features = tf.concat(
                [tf.reshape(parsed_features[k], [-1])
                 for k in dataset_definition["features"].keys()],
                axis=-1
            )
        else:
            features = {k: parsed_features[k]
                        for k in dataset_definition["features"].keys()}

        label = parsed_features[label_name]

        # Apply optional preprocessing if specified
        if "preprocessing" in dataset_definition:
            features = apply_preprocessing(
                features, dataset_definition["preprocessing"], task_logger)

        return features, label

    dataset = raw_dataset.map(_parse_function)
    return dataset.batch(batch_size).shuffle(buffer_size=1000)


def validate_model_and_dataset_definition(model, dataset_definition):
    """Validate that the model's input/output shapes match the dataset definition."""
    input_shape = model.input_shape[1:]  # Exclude batch dimension
    output_shape = model.output_shape[1:]  # Exclude batch dimension

    if input_shape != tuple(dataset_definition["input_shape"]):
        raise ValueError(
            f"Model input shape {input_shape} does not match dataset input shape {dataset_definition['input_shape']}")

    if output_shape != tuple(dataset_definition["output_shape"]):
        raise ValueError(
            f"Model output shape {output_shape} does not match dataset output shape {dataset_definition['output_shape']}")


def apply_preprocessing(features, preprocessing_steps, task_logger):
    """
    Apply preprocessing steps to the features.
    Supports normalization, scaling, and other transformations.
    """
    if preprocessing_steps.get("normalize", False):
        task_logger.info("Standardizing features (mean 0, std 1)...")
        mean = tf.reduce_mean(features, axis=0, keepdims=True)
        std = tf.math.reduce_std(features, axis=0, keepdims=True)
        features = (features - mean) / (std + 1e-8)

    if "scale" in preprocessing_steps:
        task_logger.info("Scaling features...")
        scale = preprocessing_steps["scale"]
        features = features * scale

    if "clip" in preprocessing_steps:
        task_logger.info("Clipping features...")
        min_val, max_val = preprocessing_steps["clip"]
        features = tf.clip_by_value(features, min_val, max_val)

    return features
