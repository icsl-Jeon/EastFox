from django.db import models
from django_mysql.models import ListCharField
from django.contrib.auth.models import User


class Filter(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    applied_date = models.DateField(blank=True)


class Strategist(models.Model):
    EXCHANGE_STRING_MAX_LENGTH = 10
    NAME_STRING_MAX_LENGTH = 20
    id = models.AutoField(primary_key=True, editable=False)  # NOTE: id does not create until strategist.save()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    asset_pool = ListCharField(base_field=models.CharField(max_length=EXCHANGE_STRING_MAX_LENGTH), size=4,
                               max_length=4 * (EXCHANGE_STRING_MAX_LENGTH + 1))
    from_date = models.DateField()
    to_date = models.DateField()
    name = models.CharField(max_length=NAME_STRING_MAX_LENGTH)
    filter_list = models.ManyToManyField(Filter, blank=True)


