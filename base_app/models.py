import json
import re
from datetime import datetime

import openrouteservice
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _

from base_app.ors_client import get_decoded_directions, get_reversed_polyline_directions, get_directions, \
    decode_geometry, get_isochrones


class Settings(models.Model):
    default_latitude = models.CharField(max_length=254)
    default_longitude = models.CharField(max_length=254)
    default_zoom = models.IntegerField(default=12)


class Paramedic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # django profile model
    online = models.BooleanField(default=False)
    last_latitude = models.CharField(max_length=254, null=True, blank=True)
    last_longitude = models.CharField(max_length=254, null=True, blank=True)
    last_lat_lng_update = models.DateTimeField(null=True, blank=True)
    gps_accuracy = models.FloatField(default=0)
    channel_name = models.CharField(max_length=254)

    @classmethod
    def get_by_user(cls, user):
        group, created = Group.objects.get_or_create(name='paramedics')

        if group in user.groups.all():
            obj, created = cls.objects.get_or_create(user=user)
            return obj
        return None

    def set_online(self, channel_name):
        self.online = True
        self.channel_name = channel_name
        self.save()
        self.broadcast()

    def set_offline(self):
        self.online = False
        self.channel_name = ''
        self.save()

    def update_position(self, crd):
        self.online = True
        self.last_latitude = crd.get('latitude')
        self.last_longitude = crd.get('longitude')
        self.gps_accuracy = crd.get('accuracy')
        self.last_lat_lng_update = datetime.today()
        self.save()
        if emergency_alert := self.get_active_emergency_job():
            emergency_alert.update_directions()
            emergency_alert.broadcast()
        self.broadcast()

    def get_active_emergency_job(self):
        return EmergencyAlert.objects.filter(paramedic=self, status=EmergencyAlert.EmergencyStatus.IN_PROCESS).last()

    def get_status(self):
        # IN_PROCESS when EmergencyAlert with status == IN_PROCESS and paramedic == self exists
        if EmergencyAlert.objects.filter(paramedic=self, status=EmergencyAlert.EmergencyStatus.IN_PROCESS).exists():
            return 'IN_PROCESS'
        return 'FREE'

    def get_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'online': self.online,
            'latitude': self.last_latitude,
            'longitude': self.last_longitude,
            'accuracy': self.gps_accuracy,
            'active_emergency_alert_id': self.get_active_emergency_job().id if self.get_active_emergency_job() else '',
            'last_lat_lng_update': self.last_lat_lng_update.strftime('%Y-%m-%d %H:%M') if self.last_lat_lng_update else '',
            'isochrones': self.get_isochrones_reversed() if self.last_latitude else [],
            'status': self.get_status(),
        }

    def broadcast(self):
        channel_layer = get_channel_layer()
        data = self.get_dict()
        async_to_sync(channel_layer.group_send)('base_app', {'type': 'broadcast.paramedic', 'data': data})

    @classmethod
    def get_initial_data(cls):
        # get online paramedics
        return [pm.get_dict() for pm in cls.objects.filter(online=True)]

    def get_settings(self):
        if not hasattr(self, 'paramedicsettings'):
            return ParamedicSettings.objects.get_or_create(paramedic=self)[0]
        return self.paramedicsettings

    def get_isochrones(self, _profile='driving-car', _range=300):
        return get_isochrones([(self.last_longitude, self.last_latitude)], _profile=_profile, _range=_range)['features'][0]['geometry']['coordinates'][0]

    def get_isochrones_reversed(self, _range=300):
        try:
            settings = self.get_settings()
            isochrones = [list(reversed(point)) for point in
                          self.get_isochrones(_profile=settings.routing_profile, _range=settings.isochrone_range)]
        except openrouteservice.exceptions.ApiError as api_error:
            print('Isochrones api error occured!')
            print(api_error)
            isochrones = []
        return isochrones


class ParamedicSettings(models.Model):
    class RoutingProfile(models.TextChoices):
        DRIVING_CAR = "driving-car", "Poruszanie samochodem"
        FOOT_WALKING = "foot-walking", "Poruszanie pieszo"
        CYCLING_REGULAR = "cycling-regular", "Poruszanie rowerem"

    paramedic = models.OneToOneField(Paramedic, on_delete=models.CASCADE)
    routing_profile = models.CharField(max_length=30, choices=RoutingProfile.choices, default=RoutingProfile.DRIVING_CAR)
    isochrone_range = models.IntegerField(default=120)  # in seconds


class Dispositor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # django profile model
    online = models.BooleanField(default=False)
    channel_name = models.CharField(max_length=254)

    @classmethod
    def get_by_user(cls, user):
        group, created = Group.objects.get_or_create(name='dispositors')

        if group in user.groups.all():
            obj, created = cls.objects.get_or_create(user=user)
            return obj
        return None

    def set_online(self, channel_name):
        self.online = True
        self.channel_name = channel_name
        self.save()

    def set_offline(self):
        self.online = False
        self.channel_name = ''
        self.save()

    @classmethod
    def get_initial_data(cls):
        return []


class EmergencyAlert(models.Model):
    class EmergencyStatus(models.TextChoices):
        PENDING = _('Pending')
        REJECTED = _('Rejected')
        IN_PROCESS = _('In process')
        DONE = _('Done')

    class EmergencyPriority(models.TextChoices):
        NORMAL = _('Normal')
        MEDIUM = _('Medium')
        HIGH = _('High')

    status = models.CharField(max_length=15, choices=EmergencyStatus.choices, default=EmergencyStatus.PENDING)
    priority = models.CharField(max_length=10, choices=EmergencyPriority.choices)
    start_position_latitude = models.CharField(max_length=254)
    start_position_longitude = models.CharField(max_length=254)
    end_position_latitude = models.CharField(max_length=254, null=True, blank=True)
    end_position_longitude = models.CharField(max_length=254, null=True, blank=True)
    additional_info = models.TextField()
    paramedic = models.ForeignKey(Paramedic, on_delete=models.SET_NULL, null=True, blank=True)
    date_accepted_rejected = models.DateTimeField(null=True, blank=True)
    date_finished = models.DateTimeField(null=True, blank=True)
    route_geometry = models.TextField(null=True, blank=True)
    route_duration = models.FloatField(default=0, null=True, blank=True)

    @classmethod
    def get_priority_from_number(cls, priority_number):
        return {
            1: cls.EmergencyPriority.NORMAL,
            2: cls.EmergencyPriority.MEDIUM,
            3: cls.EmergencyPriority.HIGH
        }.get(priority_number)

    @classmethod
    def create_from_api(cls, data):
        model_data = {
            'priority': cls.get_priority_from_number(int(data.get('priority'))),
            'start_position_latitude': data.get('startPositionLatitude'),
            'start_position_longitude': data.get('startPositionLongitude'),
            'additional_info': data.get('additionalInfo')
        }
        if 'endPositionLatitude' in data and 'endPositionLongitude' in data:
            model_data['end_position_latitude'] = data.get('endPositionLatitude')
            model_data['end_position_longitude'] = data.get('endPositionLongitude')

        emergency = cls(**model_data)
        emergency.save()
        # emergency.send_websocket()
        emergency.broadcast()
        return emergency

    def accept(self, paramedic):
        if not self.paramedic:
            self.paramedic = paramedic
            self.status = self.EmergencyStatus.IN_PROCESS
            self.save()
            self.broadcast()
            self.paramedic.broadcast()

    def finish(self):
        self.status = self.EmergencyStatus.DONE
        self.save()
        self.broadcast()
        self.paramedic.broadcast()

    def update_directions(self):
        if self.paramedic:
            settings = self.paramedic.get_settings()
            if self.paramedic.last_latitude:
                directions = get_directions((self.paramedic.last_longitude, self.paramedic.last_latitude),
                                            (self.start_position_longitude, self.start_position_latitude),
                                            _profile=settings.routing_profile)
                self.route_duration = directions['routes'][0]['summary']['duration']
                self.route_geometry = directions['routes'][0]['geometry']
                self.save()

    def get_directions(self):
        if self.paramedic:
            if not self.route_geometry:
                self.update_directions()
            return get_reversed_polyline_directions(decode_geometry(self.route_geometry)['coordinates'])
        return []

    def get_dict(self):
        return {
            'id': self.id,
            'latitude': self.start_position_latitude,
            'longitude': self.start_position_longitude,
            'additional_info': self.additional_info,
            'status': self.status,
            'priority': self.priority,
            'paramedic_id': self.paramedic.id if self.paramedic else '',
            'directions': self.get_directions(),
            'duration': self.route_duration,
        }

    def broadcast(self):
        channel_layer = get_channel_layer()
        data = self.get_dict()
        async_to_sync(channel_layer.group_send)('base_app', {'type': 'broadcast.emergency.alert', 'data': data})

    @classmethod
    def get_active(cls):
        return cls.objects.filter(status__in=[cls.EmergencyStatus.PENDING, cls.EmergencyStatus.IN_PROCESS])

    @classmethod
    def get_initial_data(cls):
        # return active emergency alerts (PENDING, IN_PROCESS)
        return [ea.get_dict() for ea in cls.get_active()]

    @staticmethod
    def coors_valid(coordinate):
        return True if re.match(r'^[-]?\d{1,2}(\.\d+)?$', coordinate) else False

    @staticmethod
    def api_data_valid(data):
        # validate startPosition lat, lng
        # if present validate endPosition lat, lng
        # validate priority
        # validate additionalInfo
        required_params = [
            'startPositionLatitude',
            'startPositionLongitude',
            'priority',
            'additionalInfo'
        ]

        priority_accepted_values = [1, 2, 3]

        optional_params = [
            'endPositionLatitude',
            'endPositionLongitude',
        ]

        print('validating create emergency call API data')
        print(data)

        for param in required_params:
            if not data.get(param, False):
                print('api data not valid, missing required parameters: ', param)
                return False

        if priority_val := int(data.get('priority', 0)) not in priority_accepted_values:
            print('Priority value not accepted: ', priority_val)
            return False

        for param in ['startPosition' + latlng for latlng in ['Latitude', 'Longitude']]:
            if not EmergencyAlert.coors_valid(data.get(param)):
                print('Start position coordinates are not valid!')
                return False

        if 'endPositionLatitude' in data or 'endPositionLongitude' in data:
            for param in ['endPosition' + latlng for latlng in ['Latitude', 'Longitude']]:
                if not EmergencyAlert.coors_valid(data.get(param, '')):
                    print('End position coordinates are not valid!')
                    return False

        return True
