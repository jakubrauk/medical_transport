from django.urls import path
from .consumers import BaseAppConsumer


ws_urlpatterns = [
    path('ws/base_app/', BaseAppConsumer.as_asgi())
]