from rest_framework import serializers
from .models import Strategist, Filter


class StrategistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategist
        fields = '__all__'
        exclude = []


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = '__all__'
        exclude = []
