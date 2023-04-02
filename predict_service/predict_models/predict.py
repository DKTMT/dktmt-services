import os
import sys
import json
import importlib
import pandas as pd

def run_prediction(predictor, market_data):
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
        if hasattr(module, predictor):
            func = getattr(module, predictor)
            return func(market_data)

    # If the function isn't found, raise an exception
    raise ValueError(f"Function '{predictor}' not found in subdirectory")

def run_strategies_find():
    # Get the full path to the directory containing the Python files
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_path = os.path.join(BASE_DIR, "technical_analysis")

    # Find all the Python files in the subdirectory
    file_names = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and f.endswith(".py")]
    file_names = [os.path.splitext(f)[0] for f in file_names]
    
    return file_names

def run_backtest_performance(predictor, market_data):
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
        if hasattr(module, predictor):
            func = getattr(module, predictor)
            data = [dict(zip(['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], map(float, entry))) for entry in market_data]
            correct = 0 
            incorrect = 0
            budget = 100000
            last_buy = 0
            last_trade = "sell"
            trade_count = 0

            for i in range(200, 400):
                signal = func(market_data[i-200:i])
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
    
    # If the function isn't found, raise an exception
    raise ValueError(f"Function '{predictor}' not found in subdirectory")
