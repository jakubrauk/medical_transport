from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


@shared_task
def example_task():
    print({'message': 'hello'})
    msg = {'message': 'hello'}
    async_to_sync(channel_layer.group_send)('base_app', {'type': 'send_new_data', 'text': msg})
