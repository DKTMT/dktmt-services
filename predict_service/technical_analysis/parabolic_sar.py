def parabolic_sar(market_price, acceleration: float=0.02, max_acceleration: float=0.2):
    data = market_price[-100:].copy()
    
    # Extract the high, low, and close prices from the data
    highs = [float(d[2]) for d in data]
    lows = [float(d[3]) for d in data]
    closes = [float(d[4]) for d in data]
    
    # Initialize the variables
    current_high = highs[0]
    current_low = lows[0]
    sar = current_low
    trend = 1
    ep = current_high
    sar_values = [sar]
    
    # Iterate over the data and calculate the SAR values
    for i in range(1, len(data)):
        previous_high = current_high
        previous_low = current_low
        current_high = highs[i]
        current_low = lows[i]
        previous_sar = sar
        
        # Switch the trend if necessary
        if trend == 1:
            if current_low <= previous_sar:
                trend = -1
                sar = ep
                ep = previous_high
                acceleration = 0.02
        else:
            if current_high >= previous_sar:
                trend = 1
                sar = ep
                ep = previous_low
                acceleration = 0.02
        
        # Update the SAR value
        if trend == 1:
            if current_high > ep:
                ep = current_high
                acceleration = min(acceleration + 0.02, max_acceleration)
            sar = previous_sar + acceleration * (ep - previous_sar)
            sar = min(sar, current_low, previous_low)
        else:
            if current_low < ep:
                ep = current_low
                acceleration = min(acceleration + 0.02, max_acceleration)
            sar = previous_sar - acceleration * (previous_sar - ep)
            sar = max(sar, current_high, previous_high)
        
        # Append the SAR value to the list of values
        sar_values.append(sar)
    
    # Determine the current position based on the SAR value and the close price
    current_position = "hold"
    if sar_values[-1] > closes[-1]:
        current_position = "sell"
    elif sar_values[-1] < closes[-1]:
        current_position = "buy"
    
    return current_position
