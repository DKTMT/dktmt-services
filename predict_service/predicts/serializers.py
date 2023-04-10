from rest_framework import serializers
from .models import CustomStrategy

class CustomStrategySerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomStrategy
        fields = ['id','name','method','public','anonymous','created_by','created_at','updated_at']
    