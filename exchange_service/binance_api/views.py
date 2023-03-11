import hmac
import hashlib
import requests
import json

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404

from binance_api.models import UserAPI
from binance_api.services import BinanceService
from binance_api.serializers import UserAPISerializer
from exchange_service.settings import ENCRYPTION_KEY
from exchange_service.utils import hash, encrypt, decrypt


class TestView(APIView):
    def get(self, request):
        response = Response()
        response.data = {
            'message': 'test'
        }
        return response


class UserAPIView(APIView):
    def get_object(self, email):
        hashed_email = hash(email)
        return get_object_or_404(UserAPI, hashed_email=hashed_email)

    def post(self, request):
        serializer = UserAPISerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.user_data["email"]
        user = UserAPI.objects.create(
            hashed_email=hash(email),
            exchange = serializer.data['exchange'],
            encrypted_api_key = encrypt(serializer.data['api_key']),
            encrypted_api_secret = encrypt(serializer.data['api_secret'])
        )

        response_data = {
            'email': email,
            **serializer.validated_data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def get(self, request):
        email = request.user_data["email"]
        user = self.get_object(email)

        response_data = {
            'api_key': user.api_key,
            'api_secret': user.api_secret
        }
        return Response(response_data)

    def put(self, request):
        serializer = UserAPISerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.user_data["email"]
        user = self.get_object(email)
        user.api_key = serializer.validated_data['api_key']
        user.api_secret = serializer.validated_data['api_secret']
        user.save()

        response_data = {
            'email': email,
            **serializer.validated_data
        }
        return Response(response_data)

    def delete(self, request):
        email = request.user_data["email"]
        user = self.get_object(email)
        user.delete()

        response_data = {
            'message': f"API of email: {email} deleted"
        }
        return Response(response_data)


class PortView(APIView):
    def get(self, request):
        email = request.user_data["email"]
        hashed_email = hash(email)

        try:
            user = UserAPI.objects.get(hashed_email=hashed_email)
        except UserAPI.DoesNotExist:
            raise AuthenticationFailed('User not found!')

        binance_api = BinanceService(decrypt(user.encrypted_api_key),
                                     decrypt(user.encrypted_api_secret))
        port_data = binance_api.fetch_assets({})
    
        return Response({
            "coins_possess": port_data["coins_possess"],
            "port_value":  port_data["port_value"]
        })


class OrderView(APIView):
    def authenticate_and_get_binance_api(self, request):
        email = request.user_data["email"]
        hashed_email = hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'),
                                bytes(email, 'utf-8'), digestmod=hashlib.sha256).hexdigest()
        user = UserAPI.objects.filter(hashed_email=hashed_email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        binance_api = BinanceService(decrypt(user.encrypted_api_key),
                                     decrypt(user.encrypted_api_secret))
        return binance_api

    def get(self, request):
        binance_api = self.authenticate_and_get_binance_api(request)
        orders = binance_api.fetch_orders()
        response = Response({"orders": orders})
        return response

    def post(self, request):
        binance_api = self.authenticate_and_get_binance_api(request)
        symbol = request.data.get('symbol')
        side = request.data.get('side')
        order_type = request.data.get('order_type')
        quantity = request.data.get('quantity')
        price = request.data.get('price')
        orders = binance_api.create_order(symbol, side, order_type, quantity, price)
        response = Response(orders)
        return response