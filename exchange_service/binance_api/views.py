from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed


import hmac
import hashlib
import binance
from binance_api.models import UserAPI

import json
from binance_api.services import BinanceService
# from binance_api.serializers import UserAPISerializer

from exchange_service.settings import ENCRYPTION_KEY

# test.
class TestView(APIView):
    def get(self, request):
        response = Response()
        response.data = {
            'message': 'test'
        }
        return response
    
# add new API key
class BinanceAPIView(APIView):
    @action(methods=['post'], detail=False, url_path='')
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        email = request.user_data["email"]
        exchange = body['exchange']
        api_key = body['api_key']
        api_secret = body['api_secret']
        
        client = binance.Client( api_key, api_secret)
        info = client.get_exchange_info()
        timez = info['serverTime']
        
        # hash the email and encrypt api_key and api_secret
        userAPI = UserAPI()
        hashed_email = userAPI.hash(email)
        encrypted_api_key = userAPI.encrypt(api_key)
        encrypted_api_secret = userAPI.encrypt(api_secret)
        
        UserAPI.objects.create(
            hashed_email=hashed_email,
            exchange=exchange,
            encrypted_api_key=encrypted_api_key,
            encrypted_api_secret=encrypted_api_secret
        )
        
        response = Response()
        response.data = {
            'email': email,
            'api_key': api_key,
            'exchange': exchange,
            'api_secret': api_secret
        }
        return response
    
    @action(methods=['get'], detail=False, url_path='')
    def get(self, request):
        email = request.user_data["email"]
        userAPI = UserAPI()
        hashed_email = userAPI.hash(email)
        # check from db
        user = UserAPI.objects.filter(hashed_email=hashed_email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        
        response = Response()
        response.data = {
            'api_key': user.api_key,
            'api_secret': user.api_secret
        }
        return response
    
    def put(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        email = request.user_data["email"]
        exchange = body['exchange']
        api_key = body['api_key']
        api_secret = body['api_secret']
        
        # hash the email and encrypt api_key and api_secret
        userAPI = UserAPI()
        hashed_email = userAPI.hash(email)
        encrypted_api_key = userAPI.encrypt(api_key)
        encrypted_api_secret = userAPI.encrypt(api_secret)
        
        user = UserAPI.objects.filter(hashed_email=hashed_email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        user.encrypted_api_key = encrypted_api_key;
        user.encrypted_api_secret = encrypted_api_secret;
        user.save()
        
        response = Response()
        response.data = {
            'email': email,
            'api_key': api_key,
            'exchange': exchange,
            'api_secret': api_secret
        }
        return response
    
    def delete(self, request):
        email = request.user_data["email"]
        userAPI = UserAPI()
        hashed_email = userAPI.hash(email)
        user = UserAPI.objects.filter(hashed_email=hashed_email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        user.delete()
        
        response = Response()
        response.data = {
            'message': "API of email: {} deleted".format(email)
        }
        return response

# get total portfolio value
class PortView(APIView):
    def get(self, request):
        email = request.user_data["email"]
        hashed_email = hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'), bytes(email, 'utf-8'), digestmod=hashlib.sha256).hexdigest()
        # check from db
        user = UserAPI.objects.filter(hashed_email=hashed_email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        
        binance_api = BinanceService()
        binance_api.api_key = user.api_key
        binance_api.api_secret = user.api_secret
        port_data = binance_api.fetch_assets({})

        response = Response()
        response.data = {
            "coins_possess": port_data["coins_possess"],
            "port_value":  port_data["port_value"]
        }
        return response

class OrderView(APIView):
    # get all orders (buying and selling)
    def get(self, request):
        email = request.user_data["email"]
        hashed_email = hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'), bytes(email, 'utf-8'), digestmod=hashlib.sha256).hexdigest()
        # check from db
        user = UserAPI.objects.filter(hashed_email=hashed_email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        
        binance_api = BinanceService()
        binance_api.api_key = user.api_key
        binance_api.api_secret = user.api_secret
        orders = binance_api.fetch_orders()
        
        response = Response()
        response.data = {
            'message': orders
        }
        return response
    
    # add new order
    def post(self, request):
        email = request.user_data["email"]
        hashed_email = hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'), bytes(email, 'utf-8'), digestmod=hashlib.sha256).hexdigest()
        # check from db
        user = UserAPI.objects.filter(hashed_email=hashed_email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')

        binance_api = BinanceService()
        binance_api.api_key = user.api_key
        binance_api.api_secret = user.api_secret
        
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        orders = binance_api.create_order(
            body["symbol"],
            body["side"],
            body["order_type"],
            body["quantity"],
            body["price"]
        )
        
        response = Response()
        response.data = orders
        return response
    
    # remove order
    def delete(self, request):
        response = Response()
        response.data = {
            'message': 'removed order'
        }
        return response
