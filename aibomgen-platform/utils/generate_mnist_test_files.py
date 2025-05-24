import os
import numpy as np
import tensorflow as tf
from PIL import Image
import yaml
import shutil

# Define file paths (in Downloads)
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
mnist_dataset_folder = os.path.join(downloads_folder, "mnist_dataset")
yaml_filename = os.path.join(downloads_folder, "mnist_definition.yaml")
model_filename = os.path.join(downloads_folder, "mnist_model.keras")
zip_filename = os.path.join(downloads_folder, "mnist_dataset.zip")


def save_mnist_images(images, labels, base_folder, max_per_class=500):
    """Save up to max_per_class MNIST images per class to disk in class subfolders."""
    os.makedirs(base_folder, exist_ok=True)
    class_counts = {i: 0 for i in range(10)}
    for class_idx in range(10):
        class_folder = os.path.join(base_folder, f"class_{class_idx}")
        os.makedirs(class_folder, exist_ok=True)
    for idx, (img, label) in enumerate(zip(images, labels)):
        if class_counts[label] >= max_per_class:
            continue
        img = (img * 255).astype(np.uint8)
        img_pil = Image.fromarray(img.squeeze(), mode="L")
        img_path = os.path.join(
            base_folder, f"class_{label}", f"image_{class_counts[label]}.png")
        img_pil.save(img_path)
        class_counts[label] += 1
        # Stop early if all classes are filled
        if all(count >= max_per_class for count in class_counts.values()):
            break
    print(
        f"MNIST images saved to {base_folder} (max {max_per_class} per class)")


def save_mnist_yaml_definition(yaml_path):
    """Save the dataset definition for MNIST to a YAML file."""
    dataset_definition = {
        "type": "image",
        "image_size": [28, 28],
        "input_shape": [28, 28, 3],
        "output_shape": [10],
        "preprocessing": {
            "normalize": True
        }
    }
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(dataset_definition, yaml_file)
    print(f"Dataset definition saved to {yaml_path}")


def create_mnist_model():
    """Create and train a simple CNN model for MNIST."""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(28, 28, 3)),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


def zip_dataset(dataset_folder, zip_path):
    shutil.make_archive(base_name=zip_path.replace(
        ".zip", ""), format="zip", root_dir=dataset_folder)
    print(f"Dataset zipped to {zip_path}")


# Download MNIST data
(x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
x_train = x_train.astype(np.float32) / 255.0  # Normalize to [0, 1]
x_train = np.expand_dims(x_train, -1)  # Add channel dimension

# Save images to disk (in Downloads)
save_mnist_images(x_train, y_train, mnist_dataset_folder)

# Save YAML definition (in Downloads)
save_mnist_yaml_definition(yaml_filename)

# Zip the dataset (in Downloads)
zip_dataset(mnist_dataset_folder, zip_filename)

# Create and train the model (quick train for demonstration)
model = create_mnist_model()
model.save(model_filename)
print(f"Model saved to {model_filename}")
