import numpy as np

def money_flow_index(market_price , period: int = 14, buy_threshold: int = 20, sell_threshold: int = 80) -> str:
    klines = market_price[-100:].copy()

    # Parse data to numpy arrays
    high = np.array([float(entry[2]) for entry in klines])
    low = np.array([float(entry[3]) for entry in klines])
    close = np.array([float(entry[4]) for entry in klines])
    volume = np.array([float(entry[5]) for entry in klines])

    # Calculate typical price and money flow
    typical_price = (high + low + close) / 3
    money_flow = typical_price * volume

    # Calculate positive and negative money flow
    positive_money_flow = np.zeros_like(money_flow)
    negative_money_flow = np.zeros_like(money_flow)
    for i in range(1, len(typical_price)):
        if typical_price[i] > typical_price[i-1]:
            positive_money_flow[i] = money_flow[i]
        elif typical_price[i] < typical_price[i-1]:
            negative_money_flow[i] = money_flow[i]

    # Calculate money flow ratio and money flow index
    positive_money_flow_sum = np.sum(positive_money_flow[-period:])
    negative_money_flow_sum = np.sum(negative_money_flow[-period:])
    money_flow_ratio = positive_money_flow_sum / negative_money_flow_sum
    money_flow_index = 100 - (100 / (1 + money_flow_ratio))

    # Determine buy/sell/hold signal
    if money_flow_index > sell_threshold:
        signal = "sell"
    elif money_flow_index < buy_threshold:
        signal = "buy"
    else:
        signal = "hold"

    return signal
