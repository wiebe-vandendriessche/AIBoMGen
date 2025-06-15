import os
import zipfile
from PIL import Image
import io


def generate_zip_bomb_with_png(output_path, depth=5, files_per_level=10, image_size=(100, 100)):
    """
    Generates a harmless zip bomb with dummy PNG files for educational purposes.

    Args:
        output_path (str): Path to save the zip bomb file.
        depth (int): Number of nested zip levels.
        files_per_level (int): Number of PNG files per zip level.
        image_size (tuple): Size of each dummy PNG image (width, height).
    """
    def create_dummy_png(file_path, size):
        # Create a blank white PNG image
        img = Image.new('RGB', size, color=(255, 255, 255))
        img.save(file_path, format='PNG')

    base_dir = os.path.dirname(output_path)
    os.makedirs(base_dir, exist_ok=True)

    current_zip_path = output_path
    for level in range(depth):
        with zipfile.ZipFile(current_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for i in range(files_per_level):
                dummy_file_name = f"dummy_image_{level}_{i}.png"
                dummy_file_path = os.path.join(base_dir, dummy_file_name)
                create_dummy_png(dummy_file_path, image_size)
                zf.write(dummy_file_path, arcname=dummy_file_name)
                # Clean up dummy file after adding to zip
                os.remove(dummy_file_path)

            if level < depth - 1:
                next_zip_name = f"nested_level_{level + 1}.zip"
                next_zip_path = os.path.join(base_dir, next_zip_name)
                zf.write(current_zip_path, arcname=next_zip_name)
                current_zip_path = next_zip_path

    print(f"Zip bomb dataset with PNG files generated at: {output_path}")


if __name__ == "__main__":
    from pathlib import Path

    # Define the output path in the Downloads folder
    downloads_folder = Path.home() / "Downloads"
    zip_bomb_path = downloads_folder / "zip_bomb_dataset_with_png.zip"

    # Generate the zip bomb dataset with PNG files
    generate_zip_bomb_with_png(output_path=str(
        zip_bomb_path), depth=3, files_per_level=5, image_size=(100, 100))
