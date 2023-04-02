def fibonacci_retracement(market_data):
    high = max(market_data, key=lambda x: float(x[2]))[2]  # Get the highest price
    low = min(market_data, key=lambda x: float(x[3]))[3]   # Get the lowest price
    current_price = float(market_data[-1][4])             # Get the current price

    diff = float(high) - float(low)
    level1 = float(high) - 0.236 * diff
    level2 = float(high) - 0.382 * diff
    level3 = float(high) - 0.618 * diff

    if current_price <= level3:
        return "buy"
    elif current_price <= level2:
        return "hold"
    else:
        return "sell"