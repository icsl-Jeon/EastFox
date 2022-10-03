from rest_framework import serializers
from .models import Strategist

class StrategistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategist
        fields = '__all__'
        exclude = []
