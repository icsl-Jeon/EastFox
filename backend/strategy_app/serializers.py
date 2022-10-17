from rest_framework import serializers
from .models import Strategist, Filter, Segment


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = '__all__'
        exclude = []


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = '__all__'
        exclude = []


class StrategistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategist
        fields = '__all__'
        exclude = []
