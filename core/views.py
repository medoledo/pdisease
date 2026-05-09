# core/views.py
import os
import json
from collections import defaultdict

import numpy as np  # type: ignore
import tensorflow as tf  # type: ignore
from PIL import Image  # type: ignore

from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from django.shortcuts import render

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'plant_disease_model.h5')
CLASS_NAMES_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'class_names.json')
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH, 'r') as f:
    class_names = json.load(f)


def _format_class_name(raw_name: str) -> dict:
    """Split and format a raw class name like 'Plant___Disease_Name'."""
    if '___' in raw_name:
        plant_part, disease_part = raw_name.split('___', 1)
    else:
        plant_part, disease_part = raw_name, 'Unknown'
    return {
        'plant': plant_part.replace('_', ' '),
        'disease': disease_part.replace('_', ' '),
        'is_healthy': 'healthy' in disease_part.lower(),
    }


def _build_disease_guide() -> dict:
    items = [_format_class_name(name) for name in class_names]
    guide = defaultdict(list)
    for item in items:
        guide[item['plant']].append(item)
    # Sort plants by number of diseases (descending) so the most-trained plants appear first
    return dict(sorted(guide.items(), key=lambda kv: len(kv[1]), reverse=True))


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    guide = _build_disease_guide()
    return render(request, 'index.html', {
        'disease_guide': guide,
        'total_classes': len(class_names),
    })


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
