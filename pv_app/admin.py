from django.contrib import admin

# Register your models here.
from .models import registerable_models

def register_models(registerable_models:list):
    for model in registerable_models:
        admin.site.register(model)

register_models(registerable_models)