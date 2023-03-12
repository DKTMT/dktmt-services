import json
import requests

from rest_framework.views import APIView
from rest_framework.response import Response

from .predict import get_predict_result, get_strategies


# Create your views here.
class StrategyView(APIView):
    def get(self, request):
        response = Response()
        response.data = {
            'strategies':  get_strategies()
        }
        return response
    
class PredictView(APIView):
    # params 1.coin 2.timeframe 3.exchange 4.predictor(s)
    def get(self, request):
        print(request.data)

        symbol = request.data['symbol']
        interval = request.data['timeframe']
        exchange = request.data['exchange']
        predictors = request.data['strategies']

        # get data from binance interval between 15min to 1day
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
            result = get_predict_result(predictor, market_data)
            results[predictor] = result

        response = Response()
        response.data = {
            'results': results
        }
        return response