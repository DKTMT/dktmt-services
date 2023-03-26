from orders.models import Order
from orders.serializers import OrderSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404

from binance_api.models import UserAPI
from binance_api.services import BinanceService
from binance_api.serializers import UserAPISerializer
from exchange_service.utils import hash, encrypt, decrypt


class UserAPIView(APIView):
    # Retrieve UserAPI object by hashing the email and searching for it in the database
    def get_object(self, email):
        hashed_email = hash(email)
        return get_object_or_404(UserAPI, hashed_email=hashed_email)

    # Create a new UserAPI object with the provided data
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

    # Update the UserAPI object with the provided data
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

    # Delete the UserAPI object associated with the authenticated user
    def delete(self, request):
        email = request.user_data["email"]
        user = self.get_object(email)
        user.delete()

        response_data = {
            'message': f"API of email: {email} deleted"
        }
        return Response(response_data)
    
class UserAPIValidateView(APIView):
    def get(self, request):
        email = request.user_data["email"]
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
    def get(self, request):
        orders = Order.objects.filter(exchange='binance')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.user_data["email"]
        hashed_email =  hash(email)

        try:
            user = UserAPI.objects.get(hashed_email=hashed_email)
        except UserAPI.DoesNotExist:
            raise AuthenticationFailed('User not found!')
        binance_api = BinanceService(decrypt(user.encrypted_api_key),
                                     decrypt(user.encrypted_api_secret))
        binance_api.create_order(
            symbol=serializer.validated_data['symbol'],
            side=serializer.validated_data['side'],
            quantity=serializer.validated_data['quantity'],
            price=serializer.validated_data['price'],
        )
        
        order_data = request.data
        order_data['hashed_email'] = hashed_email
        order_data['exchange'] = 'binance'

        order = Order.objects.create(**order_data)
        order_data['order_id'] = order.order_id

        return Response(order_data)
