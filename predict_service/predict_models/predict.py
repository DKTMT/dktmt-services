import os
import importlib

def predict(predictor, market_data):
    # Get the full path to the directory containing the Python files
    dir_path = os.path.dirname(os.path.abspath(__file__)) + "/technical_analysis/"

    # Find all the Python files in the subdirectory
    py_files = [f for f in os.listdir(dir_path) if f.endswith(".py")]

    # Loop through each file
    for py_file in py_files:
        # Import the module
        module_name = py_file[:-3]  # Remove the ".py" extension
        module = importlib.import_module("technical_analysis." + module_name)

        # Check if the function exists in the module
        if hasattr(module, predictor):
            func = getattr(module, predictor)
            return func(market_data)

    # If the function isn't found, raise an exception
    raise ValueError(f"Function '{predictor}' not found in subdirectory")

def get_strategies():
    dir_path = os.path.dirname(os.path.abspath(__file__)) + "/technical_analysis/"
    file_names = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    file_names = [os.path.splitext(f)[0] for f in file_names]
    return (file_names)
