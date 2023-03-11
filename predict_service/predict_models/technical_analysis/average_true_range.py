def average_true_range(market_price):
    data = market_price[-14:].copy()
    close_prices = [float(entry[4]) for entry in data]
    high_prices = [float(entry[2]) for entry in data]
    low_prices = [float(entry[3]) for entry in data]
    true_ranges = []
    for i in range(len(data)):
        high_low = high_prices[i] - low_prices[i]
        high_close = abs(high_prices[i] - close_prices[i - 1])
        low_close = abs(low_prices[i] - close_prices[i - 1])
        true_range = max(high_low, high_close, low_close)
        true_ranges.append(true_range)
    atr = sum(true_ranges) / len(true_ranges)
    last_close = float(data[-1][4])
    should_buy = last_close > atr
    should_sell = last_close < atr
    if should_buy:
        return 'buy'
    elif should_sell:
        return 'sell'
    else:
        return 'hold'
