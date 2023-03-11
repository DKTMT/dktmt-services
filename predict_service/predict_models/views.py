from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render

import requests
import json

symbol = 'BTCUSDT'
interval = '15m'
limit = 40 # 10 hours of data with 15 minute intervals

url = 'https://api.binance.com/api/v3/klines'
params = {
    'symbol': symbol,
    'interval': interval,
    'limit': limit
}

response = requests.get(url, params=params)
data = json.loads(response.text)

# Create your views here.
class StrategyView(APIView):
    def get(self, request):
        return Response()
    
class PredictView(APIView):
    # params 1.coin 2.timeframe 3.exchange 4.predictor(s)
    def get(self, request):
        symbol = request.data['coin']
        interval = request.data['timeframe']
        exchange = request.data['exchange']
        predictors = request.data['predictor']

        # get data from binance interval between 15min to 1day
        url = 'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': 200
        }
        response = requests.get(url, params=params)
        data = response.json()

        for predictor in predictors:

            print ()

        return Response()