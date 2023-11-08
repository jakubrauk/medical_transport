import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_transport.settings')

app = Celery('medical_transport')
app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.beat_schedule = {
    'example_task': {
        'task': 'base_app.tasks.example_task',
        'schedule': 10.0
    }
}


app.autodiscover_tasks()
