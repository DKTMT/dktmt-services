from typing import List

def moving_average(market_price, short_window: int = 20, long_window: int = 50) -> str:
    """
    Computes the moving averages for a given cryptocurrency and time frame from Binance API,
    and returns a signal to buy, sell, or hold based on the crossover of the moving averages.
    """
    data = market_price[-(short_window + long_window):].copy()
    
    # Extract the closing prices
    prices = [float(d[4]) for d in data]
    
    # Compute the moving averages
    ma1 = sum(prices[-short_window:]) / short_window
    ma2 = sum(prices[-long_window:]) / long_window
    
    # Check if the short moving average has crossed above the long moving average
    if ma1 > ma2:
        return 'buy'
    
    # Check if the short moving average has crossed below the long moving average
    elif ma1 < ma2:
        return 'sell'
    
    # Otherwise, hold
    else:
        return 'hold'
