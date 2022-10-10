from django.db import models


class Exchange(models.Model):
    name = models.CharField(primary_key=True, blank=False, max_length=20)


class AssetType(models.Model):
    name = models.CharField(primary_key=True, blank=False, max_length=20)


class Sector(models.Model):
    name = models.CharField(primary_key=True, blank=False, max_length=100)


class Asset(models.Model):
    is_price_okay = models.BooleanField(default=False)

    date_modified = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    symbol = models.CharField(primary_key=True, blank=False, null=False, max_length=20)
    exchange = models.ForeignKey(Exchange, on_delete=models.SET_NULL, null=True, blank=False)
    type = models.ForeignKey(AssetType, on_delete=models.SET_NULL, null=True, blank=False)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=False)

    name = models.CharField(max_length=120)
    industry = models.CharField(max_length=240)
    ipo_date = models.DateField()
