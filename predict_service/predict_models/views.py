import json
import requests

from rest_framework.views import APIView
from rest_framework.response import Response

from .predict import run_prediction, run_strategies_find, run_backtest_performance


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
