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

def run_backtest(predictor, market_data):
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
            signals = []
            true_positives = 0
            false_positives = 0
            false_negatives = 0
            hold_count = 0

            for i in range(200, 400):
                signal = func(market_data[i-200:i])
                signals.append(signal)
                if i < len(data) - 1:
                    if signal == 'buy' and data[i + 1]['close'] > data[i]['close']:
                        true_positives += 1
                    elif signal == 'buy' and data[i + 1]['close'] <= data[i]['close']:
                        false_positives += 1
                    elif signal == 'sell' and data[i + 1]['close'] < data[i]['close']:
                        true_positives += 1
                    elif signal == 'sell' and data[i + 1]['close'] >= data[i]['close']:
                        false_positives += 1
                    elif signal == 'hold':
                        hold_count += 1
                        false_negatives += 1
                    else:
                        false_negatives += 1

            total_tests = len(signals)
            accuracy = (true_positives + false_negatives) / total_tests
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) != 0 else 0
            recall = true_positives / (true_positives + false_negatives)
            buy_sell_accuracy = (true_positives + false_negatives - hold_count) / (total_tests - hold_count) if (total_tests - hold_count) != 0 else 0
            number_of_buy_sell = total_tests - hold_count;

            return {
                'number_of_tests': total_tests,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'number_of_buy_sell': number_of_buy_sell,
                'buy_sell_accuracy': buy_sell_accuracy
            }
    
    # If the function isn't found, raise an exception
    raise ValueError(f"Function '{predictor}' not found in subdirectory")