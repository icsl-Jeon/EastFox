from django.db import models
from django_mysql.models import ListCharField
from django.contrib.auth.models import User


class Filter(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    applied_date = models.DateField(blank=True)


class Strategist(models.Model):
    id = models.AutoField(primary_key=True, editable=False)  # NOTE: id does not create until strategist.save()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    from_date = models.DateField()
    to_date = models.DateField()
    name = models.CharField(max_length=40)
    filter_list = models.ManyToManyField(Filter, blank=True)

    x1 = models.FloatField(default=0.0, blank=False, null=False)
    y1 = models.FloatField(default=0.0, blank=False, null=False)
    x2 = models.FloatField(default=0.0, blank=False, null=False)
    y2 = models.FloatField(default=0.0, blank=False, null=False)
