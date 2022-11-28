import sys

sys.path.append('../')  # TODO: valid only when we start server at backend folder

from django.db import models

from django_mysql.models import ListCharField
from django.contrib.auth.models import User
from fetch.models import Asset


class Screener(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    x1 = models.FloatField(default=0.0, blank=False, null=False)
    y1 = models.FloatField(default=0.0, blank=False, null=False)
    x2 = models.FloatField(default=0.0, blank=False, null=False)
    y2 = models.FloatField(default=0.0, blank=False, null=False)


class Timeline(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    from_date = models.DateField()
    to_date = models.DateField()
    name = models.CharField(max_length=40)
    screener_list = models.ManyToManyField(Screener, blank=True, through='ScreenerApplication')

    x1 = models.FloatField(default=0.0, blank=False, null=False)
    y1 = models.FloatField(default=0.0, blank=False, null=False)
    x2 = models.FloatField(default=0.0, blank=False, null=False)
    y2 = models.FloatField(default=0.0, blank=False, null=False)


class ScreenerApplication(models.Model):
    class Meta:
        unique_together = ['user', 'timeline', 'screener', 'applied_date']

    id = models.AutoField(primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    screener = models.ForeignKey(Screener, on_delete=models.CASCADE)
    timeline = models.ForeignKey(Timeline, on_delete=models.CASCADE)
    applied_date = models.DateField(blank=True)

    x1 = models.FloatField(default=0.0, blank=False, null=False)
    y1 = models.FloatField(default=0.0, blank=False, null=False)
    x2 = models.FloatField(default=0.0, blank=False, null=False)
    y2 = models.FloatField(default=0.0, blank=False, null=False)


class Segment(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timeline = models.ForeignKey(Timeline, models.CASCADE, null=True)
    asset_list = models.ManyToManyField(Asset, blank=True)
    from_date = models.DateField()
    to_date = models.DateField()
