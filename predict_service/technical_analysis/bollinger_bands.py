import numpy as np

def bollinger_bands(market_price, window_size: int = 20, num_std_devs: int = 2):
    """
    The function bollinger_bands computes the Bollinger Bands indicator for a given market price data and generates a buy, sell, or hold signal based on the current price and the Bollinger Bands values. The Bollinger Bands consist of three lines: the middle band (usually a simple moving average), the upper band (the middle band plus a multiple of the standard deviation of the prices), and the lower band (the middle band minus a multiple of the standard deviation of the prices).

    The function takes three optional parameters:

    window_size: an integer representing the number of periods to use when calculating the Bollinger Bands. Default value is 20.
    num_std_devs: an integer representing the number of standard deviations to use when calculating the upper and lower bands. Default value is 2.
    """
    data = market_price[-window_size:].copy()
    close_prices = [float(entry[4]) for entry in data]
    std_dev = np.std(close_prices)
    middle_band = np.mean(close_prices)
    upper_band = middle_band + (num_std_devs * std_dev)
    lower_band = middle_band - (num_std_devs * std_dev)
    last_close = float(data[-1][4])
    if last_close > upper_band:
        return 'sell'
    elif last_close < lower_band:
        return 'buy'
    else:
        return 'hold'
