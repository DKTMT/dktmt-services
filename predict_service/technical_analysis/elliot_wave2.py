import pandas as pd
import numpy as np
import talib

def zigzag(high, low, close, pct_threshold=5):
    zz = talib.HT_TRENDLINE(close)
    swing_high = np.where(high > np.roll(zz, 1))[0]
    swing_low = np.where(low < np.roll(zz, 1))[0]
    zigzag_points = np.sort(np.append(swing_high, swing_low))
    
    return zigzag_points

def elliot_wave_pattern(zigzag_points, close, pct_threshold):
    if len(zigzag_points) < 7:
        return "hold"

    impulse_wave = zigzag_points[-5:]
    corrective_wave = zigzag_points[-7:]

    impulse_trend = 0
    corrective_trend = 0

    for i in range(4):
        percentage_change = (close[impulse_wave[i + 1]] - close[impulse_wave[i]]) / close[impulse_wave[i]] * 100
        if i % 2 == 0 and percentage_change > pct_threshold:
            impulse_trend += 1
        elif i % 2 == 1 and percentage_change < -pct_threshold:
            impulse_trend += 1

    for i in range(2):
        percentage_change = (close[corrective_wave[i + 1]] - close[corrective_wave[i]]) / close[corrective_wave[i]] * 100
        if i % 2 == 0 and percentage_change < -pct_threshold:
            corrective_trend += 1
        elif i % 2 == 1 and percentage_change > pct_threshold:
            corrective_trend += 1

    if impulse_trend == 4 and corrective_trend == 2:
        return "buy"
    elif impulse_trend == 3 and corrective_trend == 1:
        return "sell"
    else:
        return "hold"


def elliot_wave2(market_data):
    klines = market_data.copy()
    df = pd.DataFrame(klines, columns=["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
    df = df.astype({"open": "float64", "high": "float64", "low": "float64", "close": "float64", "volume": "float64"})

    high = df["high"].values
    low = df["low"].values
    close = df["close"].values

    pct_threshold=5
    zigzag_points = zigzag(high, low, close, pct_threshold)
    signal = elliot_wave_pattern(zigzag_points, close, pct_threshold)

    return signal
