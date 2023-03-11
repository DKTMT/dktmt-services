def triangular_moving_average(market_data):
    data = market_data.copy()
    # Calculate the triangular moving average (TMA)
    sum = 0
    weight = 1
    tma = []
    for i in range(len(data)):
        sum += float(data[i][4]) * weight
        weight += 1
        if i >= 19:
            tma.append(sum / 210)
            sum -= float(data[i-19][4])
            weight -= 20
    
    # Calculate the current price and TMA difference
    current_price = float(data[-1][4])
    tma_diff = current_price - tma[-1]
    
    # Generate a buy, sell, or hold signal based on TMA difference
    if tma_diff > 0:
        return 'buy'
    elif tma_diff < 0:
        return 'sell'
    else:
        return 'hold'
