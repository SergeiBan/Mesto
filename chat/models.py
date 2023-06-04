from django.db import models


class Spot(models.Model):
    y = models.FloatField()
    x = models.FloatField()
    channel_name = models.CharField(max_length=128)
