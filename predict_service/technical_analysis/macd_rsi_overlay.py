import pandas as pd
import talib

def macd_rsi_overlay(market_data, macd_fastperiod=12, macd_slowperiod=26, macd_signalperiod=9, rsi_timeperiod=14) -> str:
    klines = market_data.copy()

    data = pd.DataFrame(klines, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"])
    data["Close"] = pd.to_numeric(data["Close"])

    macd, signal, _ = talib.MACD(data["Close"], fastperiod=macd_fastperiod, slowperiod=macd_slowperiod, signalperiod=macd_signalperiod)
    rsi = talib.RSI(data["Close"], timeperiod=rsi_timeperiod)

    if macd.iloc[-1] > signal.iloc[-1] and rsi.iloc[-1] < 30:
        return "buy"
    elif macd.iloc[-1] < signal.iloc[-1] and rsi.iloc[-1] > 70:
        return "sell"
    else:
        return "hold"
