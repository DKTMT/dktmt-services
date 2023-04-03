import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from predict_service.utils import hash
from .predict import run_prediction, run_strategies_find, run_backtest_performance
from .models import CustomStrategy
from .serializers import CustomStrategySerializer


# Create your views here.
class StrategyView(APIView):
    def get(self, request):
        response = Response()
        response.data = {
            'strategies':  run_strategies_find()
        }
        return response
    
class PredictView(APIView):
    def post(self, request):
        symbol = request.data['symbol']
        interval = request.data['timeframe']
        exchange = request.data['exchange']
        predictors = request.data['strategies']

        url = 'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': 200
        }
        response = requests.get(url, params=params)
        market_data = response.json()

        results = {}
        for predictor in predictors:
            result = run_prediction(predictor, market_data)
            results[predictor] = result

        response = Response()
        response.data = {
            'results': results
        }
        return response
    
class BacktestView(APIView):
    def post(self, request):
        symbol = request.data['symbol']
        interval = request.data['timeframe']
        exchange = request.data['exchange']
        predictors = request.data['strategies']

        url = 'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': 400
        }
        response = requests.get(url, params=params)
        market_data = response.json()

        results = {}
        for predictor in predictors:
            result = run_backtest_performance(predictor, market_data)
            results[predictor] = result

        response = Response()
        response.data = {
            'results': results
        }
        return response

class CustomStrategyView(APIView):
    def get(self, request):
        email = request.user_data['email']
        hashed_email = hash(email)
        custom_strategies = CustomStrategy.objects.filter(hashed_email=hashed_email)
        data = [{'id': strategy.id, 'strategies': strategy.strategies, 'method': strategy.method, 'public': strategy.public, 'created_at': strategy.created_at, 'updated_at': strategy.updated_at} for strategy in custom_strategies]
        return Response(data)

    def post(self, request):
        email = request.user_data['email']
        hashed_email = hash(email)
        strategies = request.data['strategies']
        method = request.data['method']
        public = request.data['public']
        custom_strategy = CustomStrategy(hashed_email=hashed_email, strategies=strategies, method=method, public=public)
        custom_strategy.save()
        data = {'id': custom_strategy.id, 'strategies': custom_strategy.strategies, 'method': custom_strategy.method, 'public': custom_strategy.public, 'created_at': custom_strategy.created_at, 'updated_at': custom_strategy.updated_at}
        return Response(data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        email = request.user_data['email']
        hashed_email = hash(email)
        try:
            custom_strategy = CustomStrategy.objects.get(id=pk, hashed_email=hashed_email)
        except CustomStrategy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        strategies = request.data.get('strategies', custom_strategy.strategies)
        method = request.data.get('method', custom_strategy.method)
        public = request.data.get('public', custom_strategy.public)
        custom_strategy.strategies = strategies
        custom_strategy.method = method
        custom_strategy.public = public
        custom_strategy.save()
        data = {'id': custom_strategy.id, 'strategies': custom_strategy.strategies, 'method': custom_strategy.method, 'public': custom_strategy.public, 'created_at': custom_strategy.created_at, 'updated_at': custom_strategy.updated_at}
        return Response(data)

    def delete(self, request, pk):
        email = request.user_data['email']
        hashed_email = hash(email)
        try:
            custom_strategy = CustomStrategy.objects.get(id=pk, hashed_email=hashed_email)
        except CustomStrategy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        custom_strategy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)