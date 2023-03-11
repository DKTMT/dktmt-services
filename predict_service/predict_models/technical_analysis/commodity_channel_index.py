import numpy as np

def commodity_channel_index(market_price):
    data = market_price[-20:].copy()
    
    # Calculate the typical price for each period using the high, low, and close values
    typical_prices = [(float(entry[2]) + float(entry[3]) + float(entry[4])) / 3 for entry in data]
    
    # Calculate the mean price and mean deviation for the selected periods
    mean_price = np.mean(typical_prices)
    mean_deviation = np.mean(np.abs(typical_prices - mean_price))
    
    # Calculate the CCI for the most recent period
    cci = (typical_prices[-1] - mean_price) / (0.015 * mean_deviation)
    
    # Determine whether to buy, sell, or hold the cryptocurrency based on the CCI value
    if cci > 100:
        # If the CCI is above 100, it may indicate overbought conditions and suggest a sell signal
        return 'sell'
    elif cci < -100:
        # If the CCI is below -100, it may indicate oversold conditions and suggest a buy signal
        return 'buy'
    else:
        # If the CCI is between -100 and 100, it may suggest a period of stable or sideways trading
        return 'hold'