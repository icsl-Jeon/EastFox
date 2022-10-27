from rest_framework import serializers
from .models import Strategist, Filter, Segment, FilterApplication


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


class FilterApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterApplication
        fields = '__all__'
        exclude = []


class StrategistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategist
        fields = '__all__'
        exclude = []
