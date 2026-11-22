
import shutil
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "paddy_dataset"
CLEAN_PATH = BASE_DIR / "paddy_dataset_clean"

IMAGE_SIZE = (128, 128)
BATCH_SIZE = 16
EPOCHS = 10

# Create a clean dataset folder
if CLEAN_PATH.exists():
    shutil.rmtree(CLEAN_PATH)

CLEAN_PATH.mkdir(parents=True, exist_ok=True)

print("Checking Paddy images...")

valid_count = 0
invalid_count = 0

# Copy only valid images into the clean folder
for class_folder in DATASET_PATH.iterdir():

    if not class_folder.is_dir():
        continue

    destination_folder = CLEAN_PATH / class_folder.name
    destination_folder.mkdir(parents=True, exist_ok=True)

    for image_path in class_folder.rglob("*"):

        if not image_path.is_file():
            continue

        try:
            with Image.open(image_path) as img:
                img.verify()

            # Reopen and fully load the image
            with Image.open(image_path) as img:
                img.load()

            shutil.copy2(
                image_path,
                destination_folder / image_path.name
            )

            valid_count += 1

        except (UnidentifiedImageError, OSError, ValueError, PermissionError):
            invalid_count += 1
            print("Skipping invalid image:", image_path.name)

print("\nImage checking completed.")
print("Valid images:", valid_count)
print("Invalid images:", invalid_count)

if valid_count == 0:
    raise ValueError("No valid images found. Check your dataset folders.")

# Load only clean images
datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    validation_split=0.2
)

train_data = datagen.flow_from_directory(
    str(CLEAN_PATH),
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="training",
    shuffle=True
)

validation_data = datagen.flow_from_directory(
    str(CLEAN_PATH),
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="validation",
    shuffle=False
)

class_names = list(train_data.class_indices.keys())

print("\nPaddy Disease Categories:")
print(train_data.class_indices)

print("Training images:", train_data.samples)
print("Validation images:", validation_data.samples)

# Build CNN model
model = models.Sequential([
    layers.Input(shape=(128, 128, 3)),

    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D(2, 2),

    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D(2, 2),

    layers.Conv2D(128, (3, 3), activation="relu"),
    layers.MaxPooling2D(2, 2),

    layers.Flatten(),

    layers.Dense(128, activation="relu"),
    layers.Dropout(0.5),

    layers.Dense(train_data.num_classes, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print("\nStarting Paddy Disease Model Training...")

model.fit(
    train_data,
    validation_data=validation_data,
    epochs=EPOCHS
)

# Save trained model
model.save(BASE_DIR / "paddy_disease_model.keras")

# Save class names
with open(BASE_DIR / "paddy_class_names.json", "w") as file:
    json.dump(class_names, file)

print("\nPaddy model training completed!")
print("Model saved:", BASE_DIR / "paddy_disease_model.keras")