import numpy as np

def bollinger_bands(market_price):
    data = market_price[-20:].copy()
    close_prices = [float(entry[4]) for entry in data]
    std_dev = np.std(close_prices)
    middle_band = np.mean(close_prices)
    upper_band = middle_band + (2 * std_dev)
    lower_band = middle_band - (2 * std_dev)
    last_close = float(data[-1][4])
    if last_close > upper_band:
        return 'sell'
    elif last_close < lower_band:
        return 'buy'
    else:
        return 'hold'
