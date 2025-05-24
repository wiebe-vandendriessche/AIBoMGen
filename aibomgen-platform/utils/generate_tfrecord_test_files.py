import os
import pandas as pd
import numpy as np
import tensorflow as tf
import yaml

# File paths
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
dataset_filename = os.path.join(downloads_folder, "winequality.tfrecord")
yaml_filename = os.path.join(
    downloads_folder, "winequality_tfrecord_definition.yaml")
model_filename = os.path.join(
    downloads_folder, "winequality_tfrecord_model.keras")

# Download the real-life Wine Quality dataset
wine_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
df = pd.read_csv(wine_url, sep=';')

# Prepare features and labels
X = df.drop("quality", axis=1).values.astype(np.float32)
y = df["quality"].values

# Map labels to 0-based
unique_labels = np.sort(np.unique(y))
label_map = {v: i for i, v in enumerate(unique_labels)}
y = np.array([label_map[val] for val in y], dtype=np.int64)
num_classes = len(unique_labels)
num_features = X.shape[1]

# Save the TFRecord (features + label)


def _float_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))


def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


with tf.io.TFRecordWriter(dataset_filename) as writer:
    for features, label in zip(X, y):
        feature = {
            "features": _float_feature(features),
            "label": _int64_feature(label)
        }
        example = tf.train.Example(features=tf.train.Features(feature=feature))
        writer.write(example.SerializeToString())
print(f"TFRecord dataset saved to {dataset_filename}")

# Save the YAML definition
dataset_definition = {
    "type": "tfrecord",
    "input_shape": [num_features],
    "output_shape": [num_classes],
    "features": {
        "features": {
            "shape": [num_features],
            "dtype": "float32"
        }
    },
    "label": {
        "name": "label",
        "dtype": "int64"
    },
    "preprocessing": {
        "normalize": True
    }
}
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
