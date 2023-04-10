import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .predict import run_prediction, run_strategies_find, run_backtest_performance
from .models import CustomStrategy
from .serializers import CustomStrategySerializer

def get_market_data(symbol, interval, exchange):
    if exchange == "binance":
        url = 'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': 400
        }
        response = requests.get(url, params=params)
        return response.json()
    elif exchange == "bitkub":
        url = 'https://api.bitkub.com/api/market/candles'
        params = {
            'sym': symbol,
            'intervals': interval,
            'limit': 400
        }
        response = requests.get(url, params=params)
        candles = response.json()['result']
        return [[
            candle['open_time'],
            candle['open'],
            candle['high'],
            candle['low'],
            candle['close'],
            candle['volume'],
            candle['close_time'],
            candle['quote_asset_volume'],
            candle['number_of_trades'],
            candle['taker_buy_base_asset_volume'],
            candle['taker_buy_quote_asset_volume'],
            candle['ignore']
        ] for candle in candles]
    elif exchange == "forex":
        url = 'https://forex.com/api/market/candles'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': 400
        }
        response = requests.get(url, params=params)
        candles = response.json()['result']
        return [[
            candle['openTime'],
            candle['openPrice'],
            candle['highPrice'],
            candle['lowPrice'],
            candle['closePrice'],
            candle['volume'],
            candle['closeTime'],
            candle['quoteVolume'],
            candle['numberOfTrades'],
            candle['takerBuyBaseAssetVolume'],
            candle['takerBuyQuoteAssetVolume']
        ] for candle in candles]
    elif exchange == "stock":
        url = 'https://api.stock.com/api/market/candles'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': 400
        }
        response = requests.get(url, params=params)
        candles = response.json()['result']
        return [[
            candle['openTime'],
            candle['openPrice'],
            candle['highPrice'],
            candle['lowPrice'],
            candle['closePrice'],
            candle['volume'],
            candle['closeTime'],
            candle['quoteVolume'],
            candle['numberOfTrades'],
            candle['takerBuyBaseAssetVolume'],
            candle['takerBuyQuoteAssetVolume']
        ] for candle in candles]
    else:
        return None

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

        market_data = get_market_data(symbol, interval, exchange)
        base_strategies = run_strategies_find()
        results = {}
        for predictor in predictors:
            # check predictor
            if predictor in base_strategies:
                result = run_prediction(predictor, market_data)
            else:
                # find in db
                custom_strategy = get_object_or_404(CustomStrategy, name=predictor)
                custom_strategy_result = []
                for strategy in custom_strategy:
                    custom_strategy_result.push(run_prediction(strategy, market_data))

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

        market_data = get_market_data(symbol, interval, exchange)

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
        user_name = request.user_data["name"]
        strategies = CustomStrategy.objects.filter(
            created_by=user_name) | CustomStrategy.objects.filter(public=True)
        serializer = CustomStrategySerializer(strategies, many=True)
        
        for strategy in serializer.data:
            if strategy['anonymous'] and strategy['created_by'] != user_name:
                strategy['created_by'] = "anonymous"

        return Response(serializer.data)

    def post(self, request):
        data = request.data
        data['created_by'] = request.user_data["name"]
        serializer = CustomStrategySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            strategy = CustomStrategy.objects.get(pk=request.data["id"])
        except CustomStrategy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if strategy.created_by != request.user_data["name"]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = CustomStrategySerializer(strategy, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, strategy_id):
        try:
            strategy = CustomStrategy.objects.get(pk=strategy_id)
        except CustomStrategy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if strategy.created_by != request.user_data["name"]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        strategy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)