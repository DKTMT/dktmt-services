import numpy as np

def ichimoku_cloud(market_price):
    data = market_price[-52:].copy()
    closes = [float(item[4]) for item in data]
    high = max([float(item[2]) for item in data])
    low = min([float(item[3]) for item in data])
    tenkan_sen = (high + low) / 2
    kijun_sen = (max(closes[:26]) + min(closes[:26])) / 2
    senkou_span_a = (tenkan_sen + kijun_sen) / 2
    senkou_span_b = (max(closes[:52]) + min(closes[:52])) / 2

    # Determine the buy, sell or hold signal based on the Ichimoku Cloud analysis
    if senkou_span_a > senkou_span_b and closes[-1] > senkou_span_a and closes[-1] > senkou_span_b:
        return 'buy'
    elif senkou_span_a < senkou_span_b and closes[-1] < senkou_span_a and closes[-1] < senkou_span_b:
        return 'sell'
    else:
        return 'hold'