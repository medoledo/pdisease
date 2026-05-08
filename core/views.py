# core/views.py
import os
import json

import numpy as np
import tensorflow as tf
from PIL import Image

from django.http import JsonResponse
from django.shortcuts import render

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'plant_disease_model.h5')
CLASS_NAMES_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'class_names.json')
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH, 'r') as f:
    class_names = json.load(f)


def index(request):
    return render(request, 'index.html')


def predict(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({"error": "No image provided"}, status=400)

        image = Image.open(image_file)
        image = image.convert('RGB')
        image = image.resize((224, 224))

        img_array = np.array(image)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        predicted_index = int(np.argmax(predictions))
        confidence = float(np.max(predictions)) * 100.0

        disease_name = class_names[predicted_index]
        disease_name = disease_name.replace('___', ': ').replace('__', ' ').replace('_', ' ')

        return JsonResponse({
            "status": "success",
            "disease": disease_name,
            "confidence": f"{confidence:.1f}%"
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
