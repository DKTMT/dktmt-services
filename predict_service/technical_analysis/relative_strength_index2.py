import pandas as pd
import numpy as np

def relative_strength_index2(market_data, period=14, buy_threshold=30, sell_threshold=70):
    df = pd.DataFrame(market_data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = df['close'].astype(float)

    delta = df["close"].diff()
    gain, loss = delta.copy(), delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    avg_gain = gain.ewm(com=period-1, adjust=False).mean()
    avg_loss = loss.abs().ewm(com=period-1, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    last_rsi = rsi.iloc[-1]

    if last_rsi < buy_threshold:
        return "buy"
    elif last_rsi > sell_threshold:
        return "sell"
    else:
        return "hold"