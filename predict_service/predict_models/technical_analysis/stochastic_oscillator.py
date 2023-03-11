import pandas as pd

def stochastic_oscillator(market_data):
    data = market_data[-14:].copy()

    df = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"])

    # Convert string values to floats
    df["Open"] = df["Open"].astype(float)
    df["High"] = df["High"].astype(float)
    df["Low"] = df["Low"].astype(float)
    df["Close"] = df["Close"].astype(float)

    # Calculate the stochastic oscillator
    highest_high = df["High"].rolling(window=14).max()
    lowest_low = df["Low"].rolling(window=14).min()
    k_percent = 100 * (df["Close"] - lowest_low) / (highest_high - lowest_low)
    d_percent = k_percent.rolling(window=3).mean()

    # Determine the buy, sell or hold signal based on the oscillator values
    last_k_percent = k_percent.iloc[-1]
    last_d_percent = d_percent.iloc[-1]
    if last_k_percent < last_d_percent and last_k_percent < 20:
        return "buy"
    elif last_k_percent > last_d_percent and last_k_percent > 80:
        return "sell"
    else:
        return "hold"
