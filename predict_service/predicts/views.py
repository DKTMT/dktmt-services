import uuid
import requests
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .predict import run_prediction, run_strategies_find, run_backtest_performance, get_all_strategies, get_base_strategy_params
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
        base_strategy_names = run_strategies_find()
        base_strategies = []
        for strategy in base_strategy_names:
            base_strategies.append({
                "id": f'base-{strategy}',
                "name": strategy,
                "params": get_base_strategy_params(strategy)
            })
        response = Response()
        response.data = {
            'strategies': base_strategies
        }
        return response

class StrategyView(APIView):
    def get(self, request):
        user_data = json.loads(request.headers['X-User-Data'])
        user_name = user_data.get("name")
        response = Response()
        response.data = {
            'strategies':  get_all_strategies(user_name)
        }
        return response
    
class PredictView(APIView):
    def post(self, request):
        symbol, interval, exchange, strategies = (request.data[key] for key in ['symbol', 'timeframe', 'exchange', 'strategies'])

        market_data = get_market_data(symbol, interval, exchange, 200)
        user_data = json.loads(request.headers['X-User-Data'])
        user_name = user_data.get("name")
        all_strategies = get_all_strategies(user_name)

        results = []
        for strategy_id in strategies:
            results.append({
                "id": strategy_id,
                "name": next((strategy['name'] for strategy in all_strategies if strategy['id'] == strategy_id), strategy_id),
                "result": run_prediction(strategy_id, market_data)
            })

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
        symbol, interval, exchange, strategies = (request.data[key] for key in ['symbol', 'timeframe', 'exchange', 'strategies'])
        market_data = get_market_data(symbol, interval, exchange, 400)

        results = []
        for strategy_id in strategies:
            try:
                result = BacktestResult.objects.get(id=strategy_id)
            except BacktestResult.DoesNotExist:
                # If no such result exists, create a new one
                result = BacktestResult(id=strategy_id)
                if strategy_id.startswith("base-"):
                    result.name = strategy_id[len('base-'):]
                else:
                    strategy = CustomStrategy.objects.get(id=strategy_id)
                    result.name = strategy.name
            
            result.status = 'running'
            result.save()
            
             # Run the backtest and update the result fields
            backtest_data = run_backtest_performance(strategy_id, market_data)
            result.number_of_buy_sell = backtest_data['number_of_buy_sell']
            result.accuracy_of_buy_sell = backtest_data['accuracy_of_buy_sell']
            result.number_of_mock_trade = backtest_data['number_of_mock_trade']
            result.start_budget = backtest_data['start_budget']
            result.final_budget = backtest_data['final_budget']

            # Save the updated result and return a success response
            result.status = 'ready'
            result.save()
            results.append({
                "id": strategy_id,
                "name": result.name,
                'number_of_buy_sell': result.number_of_buy_sell,
                'accuracy_of_buy_sell': result.accuracy_of_buy_sell,
                'number_of_mock_trade': result.number_of_mock_trade,
                'start_budget' : result.start_budget,
                'start_budget' : result.final_budget
            })

        return Response({'results': results})

class CustomStrategyView(APIView):
    def get(self, request):
        user_data = json.loads(request.headers['X-User-Data'])
        user_name = user_data.get("name")
        strategies = CustomStrategy.objects.filter(
            created_by=user_name) | CustomStrategy.objects.filter(public=True)
        serializer = CustomStrategySerializer(strategies, many=True)
        
        all_strategies = get_all_strategies(user_name)

        for strategy in serializer.data:
            if strategy['created_by'] != user_name:
                if strategy['anonymous']:
                    strategy['created_by'] = "anonymous"
                strategy['name'] = f'{strategy["name"]} by {strategy["created_by"]}'

            method_name = strategy['method']["name"]
            if  method_name == "chain":
                print (strategy['method']["strategies"])
                strategy['method']["strategies"] = [next((strategy["name"] for strategy in all_strategies if strategy["id"] == strategy_id), strategy_id) for strategy_id in strategy['method']["strategies"]]
            elif method_name == "poll":
                for sub_strategy_id in strategy['method']["strategies"]:
                    sub_strategy_id["strategy"] = next((strategy['name'] for strategy in all_strategies if strategy['id'] == sub_strategy_id["strategy"]), sub_strategy_id["strategy"])

        response = Response()
        response.data = {
            'strategies':  serializer.data
        }
        return response

    def post(self, request):
        data = request.data
        user_data = json.loads(request.headers['X-User-Data'])
        user_name = user_data.get("name")
        custom_id = 'custom-' + str(uuid.uuid4())
        data["id"] = custom_id
        data['created_by'] = user_name
        serializer = CustomStrategySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            result = {
                "id": custom_id,
                "name": serializer.data["name"],
                "method": serializer.data["method"],
                "public": serializer.data["public"],
                "anonymous": serializer.data["anonymous"]
            }
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            strategy = CustomStrategy.objects.get(pk=request.data["id"])
        except CustomStrategy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_data = json.loads(request.headers['X-User-Data'])
        user_name = user_data.get("name")
        if strategy.created_by != user_name:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = CustomStrategySerializer(strategy, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        strategy_id = request.data["id"]
        user_data = json.loads(request.headers['X-User-Data'])
        user_name = user_data.get("name")
        try:
            strategy = CustomStrategy.objects.get(id=strategy_id)
            if strategy.created_by != user_name:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except CustomStrategy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        strategy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)