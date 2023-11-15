from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
import json

from base_app.models import Paramedic


class BaseAppConsumer(WebsocketConsumer):

    def connect(self):
        async_to_sync(self.channel_layer.group_add)('base_app', self.channel_name)
        self.accept()
        # self.send(json.dumps({'message': 'hello', 'channel_name': self.channel_name}))

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)('base_app', self.channel_name)

    def send_new_data(self, event):
        new_data = event['text']
        self.send(json.dumps(new_data))

    def broadcast_emergency_alert(self, event):
        self.send(json.dumps({'type': 'broadcast_emergency_alert', 'data': event['data']}))

    def receive(self, text_data=None, bytes_data=None):
        print('received message')
        data = json.loads(text_data)
        print(data)
        if 'data' in data:
            self.process_received(data['data']['type'], data['data']['data'])

    def process_received(self, _type, _data):
        {
            'position_update': self.position_update
        }.get(_type)(_data)

    def position_update(self, _data):
        # paramedics
        paramedic = Paramedic.get_by_user(self.scope['user'])
        if paramedic:
            paramedic.update_position(_data)
