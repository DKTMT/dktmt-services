import pandas as pd
import numpy as np

def macd(market_data, ema_short: int = 12, ema_long: int = 26, signal_period: int = 9) -> str:
    data = market_data.copy()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    # Convert timestamp to datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # Calculate the EMA
    ema_short = df['close'].ewm(span=ema_short, adjust=False).mean()
    ema_long = df['close'].ewm(span=ema_long, adjust=False).mean()
    # Calculate the MACD line and signal line
    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
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
