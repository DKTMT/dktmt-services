import numpy as np

from typing import List

def commodity_channel_index(market_price, window_size: int = 20, constant: float = 0.015, overbought: int = 100, oversold: int = -100):
    data = market_price[-window_size:].copy()
    
    # Calculate the typical price for each period using the high, low, and close values
    typical_prices = [(float(entry[2]) + float(entry[3]) + float(entry[4])) / 3 for entry in data]
    
    # Calculate the mean price and mean deviation for the selected periods
    mean_price = np.mean(typical_prices)
    mean_deviation = np.mean(np.abs(typical_prices - mean_price))
    
    # Calculate the CCI for the most recent period
    cci = (typical_prices[-1] - mean_price) / (constant * mean_deviation)
    
    # Determine whether to buy, sell, or hold the cryptocurrency based on the CCI value
    if cci > overbought:
        # If the CCI is above the overbought threshold, it may indicate overbought conditions and suggest a sell signal
        return 'sell'
    elif cci < oversold:
        # If the CCI is below the oversold threshold, it may indicate oversold conditions and suggest a buy signal
        return 'buy'
    else:
        # If the CCI is between the overbought and oversold thresholds, it may suggest a period of stable or sideways trading
        return 'hold'
