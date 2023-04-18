import os
import sys
import inspect
import importlib

from django.shortcuts import get_object_or_404

from .serializers import CustomStrategySerializer
from .models import CustomStrategy

def run_prediction(strategy_id, market_data, params=[]):
    base_strategies = run_strategies_find()
    
    if strategy_id.startswith("base-"):
        strategy_name = strategy_id[len('base-'):]
        if strategy_name in base_strategies:
                # Get the full path to the directory containing the Python files
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, os.path.join(BASE_DIR, 'technical_analysis'))

            # Find all the Python files in the subdirectory
            py_files = [f for f in os.listdir(os.path.join(BASE_DIR, 'technical_analysis')) if f.endswith(".py")]

            # Loop through each file
            for py_file in py_files:
                # Import the module
                module_name = py_file[:-3]  # Remove the ".py" extension
                module = importlib.import_module(module_name)

                # Check if the function exists in the module
                if hasattr(module, strategy_name):
                    func = getattr(module, strategy_name)
                    if params and params != []:
                        dict_params = {param["name"]: param["value"] if isinstance(param["value"], int) else int(param["value"]) for param in params}
                        return func(market_data, **dict_params)
                    return func(market_data)
    else:
        print (strategy_id)
        custom_strategy = get_object_or_404(CustomStrategy, id=strategy_id)
        method = custom_strategy.method
        if (method["name"] == "chain"):
            order = method["strategies"]
            previous_result = run_prediction(order[0], market_data)
            
            for strategy in order:
                predict_result = run_prediction(strategy, market_data)
                if (predict_result != previous_result):
                    return "hold"
                else:
                    previous_result = predict_result
            return previous_result
        
        # poll 
        elif (method["name"]== "poll"):
            poll = method["strategies"]
            result_poll = {
                "buy": 0,
                "sell": 0,
                "hold": 0
            }
            for strategy in poll:
                strategy_name = strategy["strategy"]
                strategy_vote = strategy["vote"]
                predict_result = run_prediction(strategy_name, market_data)
                result_poll[predict_result] += strategy_vote
        
        elif (method["name"]== "base"):
            strategy = method["strategy"]
            params = method["params"]
            return run_prediction( method["strategy"], market_data, params)

        return  max(result_poll, key=result_poll.get)
    # If the function isn't found, raise an exception
    raise ValueError(f"Strategy id: '{strategy_id}' not found")

def run_strategies_find():
    # Get the full path to the directory containing the Python files
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_path = os.path.join(BASE_DIR, "technical_analysis")

    # Find all the Python files in the subdirectory
    file_names = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and f.endswith(".py")]
    file_names = [os.path.splitext(f)[0] for f in file_names]
    
    return file_names

def run_backtest_performance(strategy_id, market_data):
    # Check if the function exists in the module
    data = [dict(zip(['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], map(float, entry))) for entry in market_data]
    correct = 0 
    incorrect = 0
    budget = 100000
    last_buy = 0
    last_trade = "sell"
    trade_count = 0
    data_length = len(market_data)

    for i in range(200, data_length):
        signal = run_prediction(strategy_id, market_data[i-200:i])
        # cutlost and out condition
        if (last_trade == "buy" and data[i]['close'] > last_buy*1.02):
            budget = budget + data[i]['close'];
            last_trade = "sell"
            trade_count += 1
        if (last_trade == "sell" and data[i]['close']*1.015 < last_buy):
            budget = budget - data[i]['close'];
            last_buy = data[i]['close']
            last_trade = "buy"
            trade_count += 1

        if i < len(data) - 1:
            if signal == 'buy':
                if data[i + 1]['close'] > data[i]['close']:
                    correct += 1
                else:
                    incorrect += 1
                if last_trade == "sell": 
                    budget -= data[i]['close'];
                    last_trade = "buy"
            elif signal == "sell":
                if  data[i + 1]['close'] < data[i]['close']:
                    correct += 1
                else:
                    incorrect += 1
                if last_trade == "buy": 
                    budget += data[i]['close'];
                    last_trade = "sell"

    number_of_buy_sell = correct + incorrect
    if (number_of_buy_sell > 0):
        accuracy_of_buy_sell = correct / (correct + incorrect)
    else:
        accuracy_of_buy_sell = 0

    return {
        'number_of_buy_sell': number_of_buy_sell,
        'accuracy_of_buy_sell': accuracy_of_buy_sell,
        'number_of_mock_trade': trade_count,
        'start_budget': 100000,
        'final_budget': budget
    }

def get_all_strategies(user_name):
    strategies = CustomStrategy.objects.filter(
        created_by=user_name) | CustomStrategy.objects.filter(public=True)
    custom_serializer = CustomStrategySerializer(strategies, many=True)
    
    base_serializer = run_strategies_find()
    custom_strategies = []
    for strategy in custom_serializer.data:
        if strategy['anonymous'] and strategy['created_by'] != user_name:
            strategy['created_by'] = "anonymous"
            strategy['name'] = f'{strategy["name"]} by {strategy["created_by"]}'
        custom_strategies.append({
            "id": strategy["id"],
            "name": strategy['name'],
            "params": []
        })
    base_strategies = []
    for strategy in base_serializer:
        base_strategies.append({
            "id": f'base-{strategy}',
            "name": strategy,
            "params": get_base_strategy_params(strategy)
        })
        
    return base_strategies + custom_strategies

def get_base_strategy_params(strategy):
    # Get the full path to the directory containing the Python files
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(BASE_DIR, 'technical_analysis'))

    # Find all the Python files in the subdirectory
    py_files = [f for f in os.listdir(os.path.join(BASE_DIR, 'technical_analysis')) if f.endswith(".py")]

    # Loop through each file
    for py_file in py_files:
        # Import the module
        module_name = py_file[:-3]  # Remove the ".py" extension
        module = importlib.import_module(module_name)

        # Check if the function exists in the module
        if hasattr(module, strategy):
            func = getattr(module, strategy)
            signature = inspect.signature(func)
            params = signature.parameters
            
            result = []
            for name, param in params.items():
                if param.annotation != inspect.Parameter.empty:
                    if isinstance(param.annotation, type):
                        param_type = param.annotation.__name__
                    else:
                        param_type = str(param.annotation)
                else:
                    param_type = "None"
                if param.default != inspect.Parameter.empty:
                    default_value = param.default
                else:
                    default_value = "No default"

                
                result.append({"name": name, "label":format_string(name), "type": param_type, "default": default_value})

            return result[1:]
        
def format_string(string):
    words = string.split('_')
    formatted_string = ' '.join([word.capitalize() for word in words])
    return formatted_string