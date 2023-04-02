import pandas as pd
import numpy as np
import talib

def order_blocks_and_breaker_blocks(market_data):

    swing_lookback=10
    show_last_bullish_ob=3
    show_last_bearish_ob=3
    use_candle_body=False

    klines = market_data.copy()
    data = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    data['open_time'] = pd.to_datetime(data['open_time'], unit='ms')
    data[['open', 'high', 'low', 'close']] = data[['open', 'high', 'low', 'close']].apply(pd.to_numeric)

    # Calculate swings
    high_swing = talib.MAX(data['high'], swing_lookback)
    low_swing = talib.MIN(data['low'], swing_lookback)

    # Calculate max and min based on use_candle_body
    if use_candle_body:
        max_candle = data[['close', 'open']].max(axis=1)
        min_candle = data[['close', 'open']].min(axis=1)
    else:
        max_candle = data['high']
        min_candle = data['low']

    # Implement the conversion logic here
    bullish_ob = []
    bearish_ob = []

    for index, row in data.iterrows():
        if index < swing_lookback:
            continue

        if row['close'] > high_swing[index]:
            minima = max_candle[index - 1]
            maxima = min_candle[index - 1]
            loc = data.loc[index - 1, 'open_time']

            for i in range(index - swing_lookback, index):
                minima = min(min_candle[i], minima)
                maxima = max_candle[i] if minima == min_candle[i] else maxima
                loc = data.loc[i, 'open_time'] if minima == min_candle[i] else loc

            bullish_ob.append({'top': maxima, 'btm': minima, 'loc': loc, 'breaker': False, 'break_loc': None})

        if row['close'] < low_swing[index]:
            minima = min_candle[index - 1]
            maxima = max_candle[index - 1]
            loc = data.loc[index - 1, 'open_time']

            for i in range(index - swing_lookback, index):
                maxima = max(max_candle[i], maxima)
                minima = min_candle[i] if maxima == max_candle[i] else minima
                loc = data.loc[i, 'open_time'] if maxima == max_candle[i] else loc

            bearish_ob.append({'top': maxima, 'btm': minima, 'loc': loc, 'breaker': False, 'break_loc': None})

    for ob in bearish_ob:
        if not ob['breaker']:
            if max(data['close'], data['open']) > ob['top']:
                ob['breaker'] = True
                ob['break_loc'] = data.loc[index, 'open_time']

    # Filter OBs based on show_last_bullish_ob and show_last_bearish_ob
    bullish_ob = bullish_ob[-show_last_bullish_ob:]
    bearish_ob = bearish_ob[-show_last_bearish_ob:]

    # Analyze the filtered OBs to determine the action: Buy, Hold, or Sell
    action = "hold"

    # Check the latest bullish OB for Buy signal
    if bullish_ob and not bullish_ob[-1]['breaker']:
        if data.iloc[-1]['close'] > bullish_ob[-1]['top']:
            action = "buy"

    # Check the latest bearish OB for Sell signal
    if bearish_ob and not bearish_ob[-1]['breaker']:
        if data.iloc[-1]['close'] < bearish_ob[-1]['btm']:
            action = "sell"

    return action

