import requests
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .predict import run_prediction, run_strategies_find, run_backtest_performance
from .models import BacktestResult, CustomStrategy
from .serializers import CustomStrategySerializer

def get_market_data(symbol, interval, exchange, limit):
    if exchange == "binance":
        url = 'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        response = requests.get(url, params=params)
        return response.json()
    elif exchange == "bitkub":
        url = 'https://api.bitkub.com/api/market/candles'
        params = {
            'sym': symbol,
            'intervals': interval,
            'limit': limit
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
            'limit': limit
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
            'limit': limit
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
    
class PredictInfoView(APIView):
    def get(self, request):
        response = Response()
        response.data = {
            "timeframe": ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"],
            "exchange": ["binance", "bitkub", "forex", "stock"]
        }
        return response

# Create your views here.
class BaseStrategyView(APIView):
    def get(self, request):
        response = Response()
        response.data = {
            'strategies':  run_strategies_find()
        }
        return response

class StrategyView(APIView):
    def get(self, request):
        base_strategies = run_strategies_find()
        user_name = request.user_data["name"]
        strategies = CustomStrategy.objects.filter(
            created_by=user_name) | CustomStrategy.objects.filter(public=True)
        serializer = CustomStrategySerializer(strategies, many=True)
        
        for strategy in serializer.data:
            if strategy['anonymous'] and strategy['created_by'] != user_name:
                strategy['created_by'] = "anonymous"

        custom_strategies = [f'{result["name"]} by {result["created_by"]}' for result in serializer.data]

        response = Response()
        response.data = {
            'strategies':  base_strategies + custom_strategies
        }
        return response
    
class PredictView(APIView):
    def post(self, request):
        symbol, interval, exchange, predictors = (request.data[key] for key in ['symbol', 'timeframe', 'exchange', 'strategies'])

        market_data = get_market_data(symbol, interval, exchange, 200)
        results = {}

        for predictor in predictors:
            result = run_prediction(predictor, market_data)
            results[predictor] = result

        return Response({'results': results})
    
class BacktestView(APIView):
    def get(self, request):
        # Get all backtest results with a status of "ready" or "running"
        backtest_results = BacktestResult.objects.filter(status__in=['ready', 'running'])
        serialized_results = []

        for result in backtest_results:
            serialized_result = {
                'name': result.name,
                'status': result.status,
                'last_update': result.last_update,
                'number_of_buy_sell': result.number_of_buy_sell,
                'accuracy_of_buy_sell': result.accuracy_of_buy_sell,
                'number_of_mock_trade': result.number_of_mock_trade,
                'start_budget': result.start_budget,
                'final_budget': result.final_budget
            }
            serialized_results.append(serialized_result)

        return Response(serialized_results, status=status.HTTP_200_OK)
    
    def post(self, request):
        symbol, interval, exchange, predictors = (request.data[key] for key in ['symbol', 'timeframe', 'exchange', 'strategies'])
        market_data = get_market_data(symbol, interval, exchange, 400)

        results = {}
        for predictor in predictors:
            try:
                result = BacktestResult.objects.get(name=predictor)
            except BacktestResult.DoesNotExist:
                # If no such result exists, create a new one
                result = BacktestResult(name=predictor)
            
            result.status = 'running'
            result.save()
            
             # Run the backtest and update the result fields
            backtest_data = run_backtest_performance(predictor, market_data)
            result.number_of_buy_sell = backtest_data['number_of_buy_sell']
            result.accuracy_of_buy_sell = backtest_data['accuracy_of_buy_sell']
            result.number_of_mock_trade = backtest_data['number_of_mock_trade']
            result.start_budget = backtest_data['start_budget']
            result.final_budget = backtest_data['final_budget']

            # Save the updated result and return a success response
            result.status = 'ready'
            result.save()
            results[predictor] = {
                'number_of_buy_sell': result.number_of_buy_sell,
                'accuracy_of_buy_sell': result.accuracy_of_buy_sell,
                'number_of_mock_trade': result.number_of_mock_trade,
                'start_budget' : result.start_budget,
                'start_budget' : result.final_budget
            }

        return Response({'results': results})

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

    def delete(self, request):
        strategy_name = request.data["strategy"]
        username = request.user_data["name"]
        try:
            strategy = CustomStrategy.objects.get(name=strategy_name, created_by=username)
        except CustomStrategy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        strategy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)