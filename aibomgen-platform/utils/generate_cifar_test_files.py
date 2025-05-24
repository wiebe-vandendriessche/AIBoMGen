import os
import numpy as np
import tensorflow as tf
from PIL import Image
import yaml
import shutil

downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
cifar_dataset_folder = os.path.join(downloads_folder, "cifar10_dataset")
yaml_filename = os.path.join(downloads_folder, "cifar10_definition.yaml")
model_filename = os.path.join(downloads_folder, "cifar10_model.keras")
zip_filename = os.path.join(downloads_folder, "cifar10_dataset.zip")


def save_cifar_images(images, labels, base_folder, max_per_class=5000):
    os.makedirs(base_folder, exist_ok=True)
    class_counts = {i: 0 for i in range(10)}
    for class_idx in range(10):
        class_folder = os.path.join(base_folder, f"class_{class_idx}")
        os.makedirs(class_folder, exist_ok=True)
    for idx, (img, label) in enumerate(zip(images, labels.flatten())):
        if class_counts[label] >= max_per_class:
            continue
        img_uint8 = (img * 255).astype(np.uint8)  # <-- Fix here
        img_pil = Image.fromarray(img_uint8)
        img_path = os.path.join(
            base_folder, f"class_{label}", f"image_{class_counts[label]}.png")
        img_pil.save(img_path)
        class_counts[label] += 1
        if all(count >= max_per_class for count in class_counts.values()):
            break
    print(
        f"CIFAR-10 images saved to {base_folder} (max {max_per_class} per class)")


def save_cifar_yaml_definition(yaml_path):
    dataset_definition = {
        "type": "image",
        "image_size": [32, 32],
        "input_shape": [32, 32, 3],
        "output_shape": [10],
        "preprocessing": {"normalize": True}
    }
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(dataset_definition, yaml_file)
    print(f"Dataset definition saved to {yaml_path}")


def create_cifar_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(32, 32, 3)),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
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


# Download CIFAR-10 data
(x_train, y_train), _ = tf.keras.datasets.cifar10.load_data()
x_train = x_train.astype(np.float32) / 255.0  # Normalize to [0, 1]

# Save images to disk (in Downloads)
save_cifar_images(x_train, y_train, cifar_dataset_folder, 500)

# Save YAML definition (in Downloads)
save_cifar_yaml_definition(yaml_filename)

# Zip the dataset (in Downloads)
zip_dataset(cifar_dataset_folder, zip_filename)

# Create and save the untrained model (in Downloads)
model = create_cifar_model()
model.save(model_filename)
print(f"Model saved to {model_filename}")
