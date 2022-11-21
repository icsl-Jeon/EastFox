from rest_framework import serializers
from .models import Timeline, Screener, Segment, ScreenerApplication


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = '__all__'
        exclude = []


class ScreenerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screener
        fields = '__all__'
        exclude = []


class ScreenerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenerApplication
        fields = '__all__'
        exclude = []


class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = '__all__'
        exclude = []
