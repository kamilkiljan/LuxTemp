from datetime import datetime

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework import permissions

from api.models import HourlyObservation
from api.serializers import HourlyObservationSerializer


class HourlyObservationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows HourlyObservations to be viewed.
    """

    serializer_class = HourlyObservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = HourlyObservation.objects.all()
        lat = self.request.query_params.get("lat")
        lon = self.request.query_params.get("lon")
        start_datetime = self.request.query_params.get("start_datetime")
        end_datetime = self.request.query_params.get("end_datetime")
        if lat is not None:
            queryset = queryset.filter(lat=lat)
        if lon is not None:
            queryset = queryset.filter(lon=lon)
        if start_datetime is not None:
            queryset = queryset.filter(time__gte=start_datetime)
        if end_datetime is not None:
            queryset = queryset.filter(time__lt=end_datetime)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="lat", description="Filter by latitude", required=False, type=float),
            OpenApiParameter(name="lon", description="Filter by longitude", required=False, type=float),
            OpenApiParameter(
                name="start_datetime",
                description="Filter by time greater than or equal to `start_datetime`",
                required=False,
                type=datetime,
            ),
            OpenApiParameter(
                name="end_datetime",
                description="Filter by time less than `end_datetime`",
                required=False,
                type=datetime,
            ),
        ]
    )
    def list(self, request, **kwargs):
        return super().list(request, **kwargs)
