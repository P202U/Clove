from PIL import Image
import os

image_folder = "static/images"

for filename in os.listdir(image_folder):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        image_path = os.path.join(image_folder, filename)
        with Image.open(image_path) as img:
            print(f"{filename}: {img.mode}")