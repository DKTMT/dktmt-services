import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def linear_regression(market_data):
    # Preprocess data and create DataFrame
    def prepare_data(klines_data):
        df = pd.DataFrame(klines_data, columns=["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
        df["close"] = df["close"].astype(float)
        df["returns"] = df["close"].pct_change().shift(-1)
        df.dropna(inplace=True)
        return df

    # Train Linear Regression model and make predictions
    def train_predict_linear_regression(df):
        X = df.index.values.reshape(-1, 1)
        y = df["returns"].values
        model = LinearRegression()
        model.fit(X, y)

        next_index = np.array([X[-1][0] + 1]).reshape(-1, 1)
        next_move = model.predict(next_index)

        signal = "buy" if next_move > 0.01 else ("sell" if next_move < -0.01 else "hold")
        return signal
    
    df = prepare_data(market_data)
    predictions = train_predict_linear_regression(df)

    return predictions
