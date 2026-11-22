
import json
import numpy as np
import tensorflow as tf
from PIL import Image
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "paddy_disease_model.keras"
CLASS_PATH = BASE_DIR / "paddy_class_names.json"

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_PATH, "r") as file:
    CLASS_NAMES = json.load(file)

def predict_paddy_disease(image_path):

    image = Image.open(image_path).convert("RGB")
    image = image.resize((128, 128))

    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    prediction = model.predict(image_array, verbose=0)

    predicted_index = int(np.argmax(prediction[0]))

    disease = CLASS_NAMES[predicted_index]

    confidence = float(prediction[0][predicted_index]) * 100

    precautions = {
        "Bacterialblight": [
            "Use certified disease-free seeds.",
            "Avoid excessive nitrogen fertilizer.",
            "Maintain proper field drainage.",
            "Consult an agriculture officer for treatment."
        ],
        "Blast": [
            "Use resistant rice varieties.",
            "Avoid excessive nitrogen fertilizer.",
            "Maintain proper field conditions.",
            "Consult an agriculture officer for treatment."
        ],
        "Brownspot": [
            "Maintain balanced soil nutrients.",
            "Use healthy seeds.",
            "Improve field management.",
            "Consult an agriculture officer for treatment."
        ],
        "Tungro": [
            "Remove infected plants as advised locally.",
            "Monitor green leafhopper populations.",
            "Use resistant rice varieties.",
            "Consult an agriculture officer for management."
        ]
    }

    return {
        "disease": disease,
        "confidence": round(confidence, 2),
        "precautions": precautions.get(disease, [])
    }