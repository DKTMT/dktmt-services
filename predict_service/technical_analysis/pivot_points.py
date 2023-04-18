import numpy as np

def pivot_points(market_data, num_periods: int = 12) -> str:
    data = market_data[-num_periods:].copy()
    # Extract the closing prices from the API response
    closes = [float(entry[4]) for entry in data]

    # Calculate the pivot points
    high = max(closes)
    low = min(closes)
    close = closes[-1]
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    r2 = pivot + (high - low)
    s1 = 2 * pivot - high
    s2 = pivot - (high - low)

    # Determine whether to buy, sell, or hold based on the pivot points
    if close > pivot and close > r1:
        return 'sell'
    elif close > pivot and close < r1:
        return 'hold'
    elif close < pivot and close < s1:
        return 'buy'
    elif close < pivot and close > s1:
        return 'hold'
    else:
        return 'hold'
