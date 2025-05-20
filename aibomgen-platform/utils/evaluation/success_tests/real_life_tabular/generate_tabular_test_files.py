import os
import pandas as pd
import numpy as np
import tensorflow as tf
import yaml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# File paths
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
dataset_filename = os.path.join(downloads_folder, "winequality.csv")
yaml_filename = os.path.join(downloads_folder, "winequality_definition.yaml")
model_filename = os.path.join(downloads_folder, "winequality_model.keras")

# Download the real-life Wine Quality dataset
wine_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
df = pd.read_csv(wine_url, sep=';')

# Prepare features and labels
X = df.drop("quality", axis=1).values
y = df["quality"].values

# For demonstration, treat quality as a multi-class label (usually 3-8)
num_classes = len(np.unique(y))
num_features = X.shape[1]

# Save the CSV (features + label)
df.to_csv(dataset_filename, index=False)
print(f"Dataset saved to {dataset_filename}")

# Save the YAML definition
dataset_definition = {
    "input_shape": [num_features],
    "output_shape": [num_classes],
    "columns": {col: "float" for col in df.columns if col != "quality"},
    "label": "quality",
    "preprocessing": {
        "normalize": True
    }
}
dataset_definition["columns"]["quality"] = "int"
with open(yaml_filename, "w") as yaml_file:
    yaml.dump(dataset_definition, yaml_file)
print(f"Dataset definition saved to {yaml_filename}")

# Build and save a simple model


def create_wine_model(input_shape, num_classes):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=input_shape),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


model = create_wine_model((num_features,), num_classes)
model.save(model_filename)
print(f"Model saved to {model_filename}")
