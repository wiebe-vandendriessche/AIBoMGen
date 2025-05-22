import os
import tensorflow as tf
import numpy as np

# Ensure TensorFlow 2.19 is being used
print(f"TensorFlow version: {tf.__version__}")

# Define file paths
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
model_filename = os.path.join(downloads_folder, "model.keras")
dataset_filename = os.path.join(downloads_folder, "dataset.tfrecord")

# Create a simple model (a basic Sequential model)
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Generate a synthetic dataset (features: 10, labels: binary classification)
def generate_synthetic_data(num_samples=1000):
    features = np.random.rand(num_samples, 10).astype(np.float32)  # 10 feature columns
    labels = np.random.randint(0, 2, size=(num_samples, 1)).astype(np.int64)  # Binary labels
    return features, labels

# Save the synthetic dataset to TFRecord
def save_tfrecord(dataset_path, num_samples=1000):
    features, labels = generate_synthetic_data(num_samples)

    with tf.io.TFRecordWriter(dataset_path) as writer:
        for feature, label in zip(features, labels):
            # Convert the data to tf.train.Example
            feature_dict = {
                'feature': tf.train.Feature(float_list=tf.train.FloatList(value=feature.flatten())),
                'label': tf.train.Feature(int64_list=tf.train.Int64List(value=label))
            }
            example = tf.train.Example(features=tf.train.Features(feature=feature_dict))
            writer.write(example.SerializeToString())

# Save model to the Downloads folder
model.save(model_filename)

# Save the synthetic dataset to a TFRecord file
save_tfrecord(dataset_filename)

print(f"Model saved to {model_filename}")
print(f"Dataset saved to {dataset_filename}")