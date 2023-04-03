from rest_framework import serializers
from .models import CustomStrategy

class CustomStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomStrategy
        fields = ['id', 'strategies', 'method', 'created_at', 'updated_at']