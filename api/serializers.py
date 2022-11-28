from api.models import HourlyObservation
from rest_framework import serializers


class HourlyObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourlyObservation
        fields = "__all__"
