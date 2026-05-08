# core/urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/predict/', csrf_exempt(views.predict), name='predict'),
]
