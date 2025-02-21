import tensorflow as tf
import numpy as np
import os

# Define dataset directory inside the mounted volume
DATASET_DIR = "/user_mounted_data/mnist_data"

# Load dataset from mounted directory
print(f"Loading dataset from: {DATASET_DIR}")
train_images = np.load(os.path.join(DATASET_DIR, "train_images.npy"))
train_labels = np.load(os.path.join(DATASET_DIR, "train_labels.npy"))

# Normalize data
train_images = train_images / 255.0

# Define a simple model
model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
model.fit(train_images, train_labels, epochs=5)

# Save the model inside the container output folder
model.save("/output/model3.keras")

print("Training complete. Model saved to /output/model3.keras")
