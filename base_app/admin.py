from django.contrib import admin
from django.apps import apps

base_app_models = apps.get_app_config('base_app').get_models()

for model in base_app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
