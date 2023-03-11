from rest_framework import serializers

class UserAPISerializer(serializers.Serializer):
    exchange = serializers.CharField()
    api_key = serializers.CharField()
    api_secret = serializers.CharField()
