import re
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


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
    paramedic = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_accepted_rejected = models.DateTimeField(null=True, blank=True)
    date_finished = models.DateTimeField(null=True, blank=True)

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
