import pandas as pd
import numpy as np

def macd(market_data):
    data = market_data.copy()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    # Convert timestamp to datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # Calculate the 12-day and 26-day EMA
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    # Calculate the MACD line and signal line
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    # Calculate the MACD histogram
    macd_hist = macd_line - signal_line
    # Determine buy, sell or hold signal
    if macd_hist.iloc[-1] > 0 and macd_hist.iloc[-2] <= 0:
        signal = 'buy'
    elif macd_hist.iloc[-1] < 0 and macd_hist.iloc[-2] >= 0:
        signal = 'sell'
    else:
        signal = 'hold'
    return signal
