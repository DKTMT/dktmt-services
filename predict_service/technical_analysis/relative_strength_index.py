import pandas as pd

def relative_strength_index(market_data, period: int = 14, buy_threshold: float = 30.0, sell_threshold: float = 70.0) -> str:
    data = pd.DataFrame(market_data[-period:].copy())
    data.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    data = data.astype({'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': float})

    # Calculate changes in price and create a new column for it
    data['Change'] = data['Close'].diff()

    # Create new columns for positive and negative price changes
    data['Positive'] = data['Change'].apply(lambda x: x if x > 0 else 0)
    data['Negative'] = data['Change'].apply(lambda x: -x if x < 0 else 0)

    # Calculate average gains and losses over the specified period
    avg_gain = data['Positive'].rolling(window=period).mean()
    avg_loss = data['Negative'].rolling(window=period).mean()

    # Calculate relative strength
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs.iloc[-1]))

    # Determine buy, sell or hold based on RSI value
    if rsi >= sell_threshold:
        return 'sell'
    elif rsi <= buy_threshold:
        return 'buy'
    else:
        return 'hold'
