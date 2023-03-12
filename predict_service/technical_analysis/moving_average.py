def moving_average(market_price):
    """
    Computes the moving averages for a given cryptocurrency and time frame from Binance API,
    and returns a signal to buy, sell, or hold based on the crossover of the moving averages.
    """
    data = market_price[-100:].copy()
    
    # Extract the closing prices
    prices = [float(d[4]) for d in data]
    
    # Compute the moving averages
    ma1 = sum(prices[-20:]) / 20
    ma2 = sum(prices[-50:]) / 50
    
    # Check if the short moving average has crossed above the long moving average
    if ma1 > ma2:
        return 'buy'
    
    # Check if the short moving average has crossed below the long moving average
    elif ma1 < ma2:
        return 'sell'
    
    # Otherwise, hold
    else:
        return 'hold'
