import os
import tensorflow as tf
import numpy as np
import pandas as pd
import yaml

# Ensure TensorFlow 2.19 is being used
print(f"TensorFlow version: {tf.__version__}")

# Define file paths
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
model_filename = os.path.join(downloads_folder, "model2.keras")
dataset_filename = os.path.join(downloads_folder, "dataset2.csv")
yaml_filename = os.path.join(downloads_folder, "definition2.yaml")


def generate_multiclass_data(num_features, num_classes, num_samples=1000):
    """Generate synthetic data for multi-class classification."""
    features = np.random.rand(num_samples, num_features).astype(np.float32)  # 20 feature columns
    labels = np.random.randint(0, num_classes, size=(num_samples,)).astype(np.int64)  # Multi-class labels
    return features, labels

def save_multiclass_csv(dataset_path, num_features, num_classes, num_samples=1000):
    """Save the synthetic multi-class dataset to a CSV file."""
    features, labels = generate_multiclass_data(num_features, num_classes, num_samples)

    # Create a DataFrame
    feature_columns = [f"feature{i+1}" for i in range(num_features)]
    df = pd.DataFrame(features, columns=feature_columns)
    df["label"] = labels

    # Save to CSV
    df.to_csv(dataset_path, index=False)
    print(f"Dataset saved to {dataset_path}")

def save_yaml_definition(yaml_path, num_features, num_classes):
    """Save the dataset definition to a YAML file."""
    dataset_definition = {
        "input_shape": [num_features],  # Number of features
        "output_shape": [num_classes],  # Number of classes
        "columns": {f"feature{i+1}": "float" for i in range(num_features)},
        "label": "label",
        "preprocessing": {
            "normalize": True,
            "scale": 1.0,
            "clip": [0.0, 1.0]
        }
    }
    dataset_definition["columns"]["label"] = "int"  # Add label column

    # Save to YAML
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(dataset_definition, yaml_file)
    print(f"Dataset definition saved to {yaml_path}")
            
def create_multiclass_model(input_shape, num_classes):
    """Create a simple multi-class classification model."""
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_shape=input_shape),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(num_classes, activation='sigmoid'),  # Use 'softmax' binary classification
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# Create and save the model
num_features = 13  # Number of features
input_shape = (num_features,) # Input shape for the model
num_classes = 1  # Number of classes (for multi-class classification)
model = create_multiclass_model(input_shape, num_classes)
model.save(model_filename)
print(f"Model saved to {model_filename}")

# Save the dataset and YAML definition
save_multiclass_csv(dataset_filename, num_features, num_classes, 1000)
save_yaml_definition(yaml_filename, num_features, num_classes)