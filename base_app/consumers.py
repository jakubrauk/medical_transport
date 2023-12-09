from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
import json

from base_app.models import Paramedic, EmergencyAlert, Dispositor


class BaseAppConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)('base_app', self.channel_name)
        if user := self.scope['user']:
            if paramedic := Paramedic.objects.filter(user=user).last():
                paramedic.set_online(self.channel_name)
            elif dispositor := Dispositor.objects.filter(user=user).last():
                dispositor.set_online(self.channel_name)

        self.accept()
        initial_data = {
            'paramedics': Paramedic.get_initial_data(),
            'emergency_alerts': EmergencyAlert.get_initial_data(),
            'dispositors': Dispositor.get_initial_data(),
            'channel_name': self.channel_name,
        }
        self.send(json.dumps({'type': 'load_initial_data', 'data': initial_data}))

    def disconnect(self, code):
        if paramedic := Paramedic.objects.filter(channel_name=self.channel_name).last():
            paramedic.set_offline()
        elif dispositor := Dispositor.objects.filter(channel_name=self.channel_name).last():
            dispositor.set_offline()
        async_to_sync(self.channel_layer.group_discard)('base_app', self.channel_name)

    def send_new_data(self, event):
        new_data = event['text']
        self.send(json.dumps(new_data))

    def broadcast_emergency_alert(self, event):
        self.send(json.dumps({'type': 'broadcast_emergency_alert', 'data': event['data']}))

    def broadcast_paramedic(self, event):
        self.send(json.dumps({'type': 'paramedic_update', 'data': event['data']}))

    def receive(self, text_data=None, bytes_data=None):
        print('received message')
        data = json.loads(text_data)
        print(data)
        if 'data' in data:
            self.process_received(data['data']['type'], data['data']['data'])

    def process_received(self, _type, _data):
        {
            'position_update': self.position_update,
            'emergency_alert_accept': self.emergency_alert_accept,
            'emergency_alert_finish': self.emergency_alert_finish,
            'create_emergency_alert': self.create_emergency_alert,
            'test_button': self.test_button_receive
        }.get(_type)(_data)

    def position_update(self, _data):
        # paramedics
        paramedic = Paramedic.get_by_user(self.scope['user'])
        if paramedic:
            paramedic.update_position(_data)

    def test_button_receive(self, _data):
        print('test button receive')
        print(_data)

    def emergency_alert_accept(self, _data):
        emergency_alert = EmergencyAlert.objects.get(id=_data.get('emergency_alert_id'))
        paramedic = Paramedic.objects.get(id=_data.get('paramedic_id'))
        emergency_alert.accept(paramedic)
        # self.send(json.dumps({'type': 'emergency_alert_directions', 'data': emergency_alert.get_directions()}))

    def emergency_alert_finish(self, _data):
        emergency_alert = EmergencyAlert.objects.get(id=_data.get('emergency_alert_id'))
        emergency_alert.finish()

    def create_emergency_alert(self, _data):
        EmergencyAlert.create_from_api(_data)
