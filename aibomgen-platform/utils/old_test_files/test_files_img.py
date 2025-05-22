import os
import tensorflow as tf
import numpy as np
import yaml
from PIL import Image
import shutil

# Ensure TensorFlow 2.19 is being used
print(f"TensorFlow version: {tf.__version__}")

# Define file paths
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
image_dataset_folder = os.path.join(downloads_folder, "image_dataset")
yaml_filename = os.path.join(downloads_folder, "image_definition.yaml")
model_filename = os.path.join(downloads_folder, "image_model.keras")
zip_filename = os.path.join(downloads_folder, "image_dataset.zip")

def generate_image_data(num_classes, num_samples_per_class, image_size=(64, 64)):
    """Generate synthetic image data for multi-class classification."""
    os.makedirs(image_dataset_folder, exist_ok=True)
    for class_idx in range(num_classes):
        class_folder = os.path.join(image_dataset_folder, f"class_{class_idx}")
        os.makedirs(class_folder, exist_ok=True)
        for sample_idx in range(num_samples_per_class):
            # Generate a random image
            image = np.random.randint(0, 256, size=(*image_size, 3), dtype=np.uint8)
            image_path = os.path.join(class_folder, f"image_{sample_idx}.png")
            Image.fromarray(image).save(image_path)
    print(f"Image dataset saved to {image_dataset_folder}")

def save_image_yaml_definition(yaml_path, image_size, num_classes):
    """Save the dataset definition for an image dataset to a YAML file."""
    dataset_definition = {
        "type": "image",
        "image_size": list(image_size),
        "input_shape": list(image_size) + [3],  # Include channels
        "output_shape": [num_classes],
        "preprocessing": {
            "normalize": True
        }
    }

    # Save to YAML
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(dataset_definition, yaml_file)
    print(f"Dataset definition saved to {yaml_path}")

def create_cnn_model(input_shape, num_classes):
    """Create a simple CNN model for image classification."""
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def zip_image_dataset(dataset_folder, zip_path):
    """Compress the image dataset folder into a .zip file."""
    shutil.make_archive(base_name=zip_path.replace(".zip", ""), format="zip", root_dir=dataset_folder)
    print(f"Image dataset zipped to {zip_path}")

# Parameters for the dataset and model
image_size = (64, 64)  # Image dimensions (height, width)
num_classes = 3  # Number of classes
num_samples_per_class = 100  # Number of images per class
input_shape = (*image_size, 3)  # Input shape for the model

# Generate and save the image dataset
generate_image_data(num_classes, num_samples_per_class, image_size)

# Save the YAML definition
save_image_yaml_definition(yaml_filename, image_size, num_classes)

# Zip the dataset
zip_image_dataset(image_dataset_folder, zip_filename)

# Create and save the CNN model
model = create_cnn_model(input_shape, num_classes)
model.save(model_filename)
print(f"Model saved to {model_filename}")