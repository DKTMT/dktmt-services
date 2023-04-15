from rest_framework import serializers

class UserAPISerializer(serializers.Serializer):
    exchange = serializers.CharField()
    api_key = serializers.CharField()
    api_secret = serializers.CharField()

class OrderSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=255)
    side = serializers.CharField(max_length=255)
    quantity = serializers.DecimalField(max_digits=20, decimal_places=8)
    price = serializers.DecimalField(max_digits=20, decimal_places=8)
