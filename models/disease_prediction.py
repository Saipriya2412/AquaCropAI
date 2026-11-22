
import tensorflow as tf
import numpy as np
from PIL import Image

MODEL_PATH = "models/maize_disease_model.keras"

model = tf.keras.models.load_model(MODEL_PATH)

CLASS_NAMES = [
    "Cercospora Leaf Spot",
    "Common Rust",
    "Northern Leaf Blight",
    "Healthy"
]


def predict_disease(image_path):

    image = Image.open(image_path).convert("RGB")
    image = image.resize((128, 128))

    image_array = np.array(image)
    image_array = image_array / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    prediction = model.predict(image_array)

    predicted_index = np.argmax(prediction[0])

    disease = CLASS_NAMES[predicted_index]

    confidence = float(prediction[0][predicted_index]) * 100

    precautions = {
        "Cercospora Leaf Spot": [
            "Monitor leaves for new spots.",
            "Remove severely affected plant material where appropriate.",
            "Avoid excessive leaf wetness.",
            "Consult a local agricultural expert for disease management."
        ],

        "Common Rust": [
            "Monitor leaves for orange-brown rust spots.",
            "Check nearby plants for symptoms.",
            "Maintain proper field sanitation.",
            "Consult an agricultural expert about suitable management."
        ],

        "Northern Leaf Blight": [
            "Inspect plants for elongated leaf lesions.",
            "Remove heavily infected crop residues where appropriate.",
            "Avoid working in wet fields when possible.",
            "Consult an agricultural expert for suitable management."
        ],

        "Healthy": [
            "Continue regular crop monitoring.",
            "Maintain appropriate irrigation.",
            "Use balanced crop nutrition.",
            "Inspect leaves regularly for early symptoms."
        ]
    }

    return {
        "disease": disease,
        "confidence": round(confidence, 2),
        "precautions": precautions[disease]
    }
