def average_true_range2(market_data):
    # Extract the closing prices from the market data
    prices = [float(entry[4]) for entry in market_data]
    
    # Calculate the true range for each period
    true_ranges = []
    for i in range(1, len(prices)):
        high = float(market_data[i][2])
        low = float(market_data[i][3])
        prev_close = float(market_data[i-1][4])
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)
    
    # Calculate the average true range over the last 14 periods
    atr = sum(true_ranges[-14:]) / 14
    
    # Calculate the buy and sell thresholds based on the ATR
    buy_threshold = atr * 1.25
    sell_threshold = atr * 0.75
    
    # Determine the current trend based on the closing price and ATR values
    last_price = prices[-1]
    if last_price > buy_threshold:
        return "buy"
    elif last_price < sell_threshold:
        return "sell"
    else:
        return "hold"