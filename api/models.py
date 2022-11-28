from django.db import models


class HourlyObservation(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    time = models.DateTimeField()
    temperature_2m = models.FloatField()
    apparent_temperature = models.FloatField()
    apparent_diff = models.FloatField()
    daily_max = models.FloatField()
    daily_min = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["lat", "lon", "time"], name="unique_observation_per_time_and_location")
        ]
