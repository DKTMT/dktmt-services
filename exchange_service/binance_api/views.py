import requests
import json
from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db import transaction

from exchange_service.utils import encrypt, decrypt

from .models import UserAPI, Order
from .serializers import UserAPISerializer, OrderSerializer
from .services import BinanceService

class UserAPIView(APIView):
    # Retrieve UserAPI object by hashing the email and searching for it in the database
    def get_object(self, email):
        hashed_email = hash(email)
        return get_object_or_404(UserAPI, hashed_email=hashed_email)

    # Create a new UserAPI object with the provided data
    def post(self, request):
        serializer = UserAPISerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get("email")
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

    # Update the UserAPI object with the provided data
    def put(self, request):
        serializer = UserAPISerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get("email")
        user = self.get_object(email)
        user.api_key = encrypt(serializer.data['api_key']),
        user.api_secret = encrypt(serializer.data['api_secret'])
        user.save()

        response_data = {
            'email': email,
            **serializer.validated_data
        }
        return Response(response_data)

    # Delete the UserAPI object associated with the authenticated user
    def delete(self, request):
        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get("email")
        user = self.get_object(email)
        user.delete()

        response_data = {
            'message': f"API of email: {email} deleted"
        }
        return Response(response_data)

class UserAPIValidateView(APIView):
    def get(self, request):
        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get("email")
        hashed_email = hash(email)
        try:
            user = UserAPI.objects.get(hashed_email=hashed_email)
        except UserAPI.DoesNotExist:
            raise AuthenticationFailed('User not found!')
        binance_api = BinanceService(decrypt(user.encrypted_api_key),
                                     decrypt(user.encrypted_api_secret))
        response_data = {"result" : binance_api.validate_binance_api()}
        return Response(response_data)
    
    def post(self, request):
        binance_api = BinanceService(request.data["api_key"],request.data["api_secret"])
        response_data = {"result" : binance_api.validate_binance_api()}
        return Response(response_data)

class PortView(APIView):
    def get(self, request):
        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get("email")
        hashed_email = hash(email)

        try:
            user = UserAPI.objects.get(hashed_email=hashed_email)
        except UserAPI.DoesNotExist:
            raise AuthenticationFailed('User not found!')

        binance_api = BinanceService(decrypt(user.encrypted_api_key),
                                     decrypt(user.encrypted_api_secret))
        port_data = binance_api.fetch_assets({})

        # Fetch icons using the Coingecko API
        icon_api = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
        try:
            response = requests.get(icon_api)
            response.raise_for_status()
            icons_data = response.json()
            icons_map = {coin["symbol"].upper(): coin["image"] for coin in icons_data}
        except requests.exceptions.RequestException as e:
            icons_map = {}

        for coin in port_data["coins_possess"]:
            asset = coin["asset"]
            coin["icon"] = icons_map.get(asset, "")

        return Response({
            "coins_possess": port_data["coins_possess"],
            "port_value":  port_data["port_value"]
        })


class OrderView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get("email")
        hashed_email = hash(email)

        try:
            user = UserAPI.objects.get(hashed_email=hashed_email)
        except UserAPI.DoesNotExist:
            raise AuthenticationFailed('User not found!')

        binance_api = BinanceService(decrypt(user.encrypted_api_key),
                                     decrypt(user.encrypted_api_secret))

        # Create the order using the Binance API
        binance_api.create_order(
            symbol=serializer.validated_data['symbol'],
            side=serializer.validated_data['side'],
            quantity=serializer.validated_data['quantity'],
            price=serializer.validated_data['price'],
        )

        # Save the order to the database
        order_data = serializer.validated_data
        order_data['hashed_email'] = hashed_email
        order_data['exchange'] = 'binance'
        order = Order.objects.create(**order_data)
        order_data['order_id'] = order.order_id

        # Serialize the created order object
        serialized_order = OrderSerializer(order)

        return Response(serialized_order.data)

    def get(self, request):
        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get("email")
        hashed_email = hash(email)
        orders = Order.objects.filter(exchange='binance', hashed_email=hashed_email)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class PortHistoryView(APIView):
    def get(self, request):
        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get("email")
        hashed_email = hash(email)
        range_days = 7

        try:
            user = UserAPI.objects.get(hashed_email=hashed_email)
        except UserAPI.DoesNotExist:
            raise AuthenticationFailed('User not found!')

        binance_api = BinanceService(decrypt(user.encrypted_api_key),
                                     decrypt(user.encrypted_api_secret))

        # Fetch historical portfolio data from the Binance API
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = end_time - (86400 * range_days * 1000)
        port_history = binance_api.fetch_port_history(start_time, end_time)
        processed_snapshots = binance_api.process_snapshots(port_history)

        result = {
            "code": 200,
            "msg": "",
            "snapshotVos": processed_snapshots
        }

        return Response(result)