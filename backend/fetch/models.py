from django.db import models


class Exchange(models.Model):
    name = models.CharField(primary_key=True, blank=False, max_length=20)


class AssetType(models.Model):
    name = models.CharField(primary_key=True, blank=False, max_length=20)


class Asset(models.Model):
    date_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    symbol = models.CharField(primary_key=True, blank=False, null=False, max_length=20)
    exchange = models.ForeignKey(Exchange, on_delete=models.SET_NULL, null=True, blank=False)
    type = models.ForeignKey(AssetType, on_delete=models.SET_NULL, null=True, blank=False)

    name = models.CharField(max_length=120)
    sector = models.CharField(max_length=120)
    industry = models.CharField(max_length=240)
    ipo_date = models.DateField()
