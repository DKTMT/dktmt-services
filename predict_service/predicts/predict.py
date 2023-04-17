import os
import sys
import importlib

from django.shortcuts import get_object_or_404

from .models import CustomStrategy

def run_prediction(strategy_id, market_data):
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

        return  max(result_poll, key=result_poll.get)
    # If the function isn't found, raise an exception
    raise ValueError(f"Function '{strategy}' not found in subdirectory")

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
