from typing import List

def fibonacci_retracement(market_data, level1: float = 0.236, level2: float = 0.382, level3: float = 0.618) -> str:
    high = max(market_data, key=lambda x: x[2])[2]  # Get the highest price
    low = min(market_data, key=lambda x: x[3])[3]   # Get the lowest price
    current_price = market_data[-1][4]             # Get the current price

    diff = float(high) - float(low)
    level1_price = float(high) - level1 * diff
    level2_price = float(high) - level2 * diff
    level3_price = float(high) - level3 * diff

    if current_price <= level3_price:
        return "buy"
    elif current_price <= level2_price:
        return "hold"
    else:
        return "sell"
