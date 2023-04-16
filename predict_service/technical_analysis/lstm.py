import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

def lstm(market_data):
    data = market_data.copy()

    data = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    data = data.astype(float)
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)

    # Define function to create buy, sell, or hold signals based on predicted prices
    def get_signal(predictions):
        signal = []
        for i in range(1, len(predictions)):
            if predictions[i] > predictions[i-1]:
                signal.append('buy')
            elif predictions[i] < predictions[i-1]:
                signal.append('sell')
            else:
                signal.append('hold')
        return signal

    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['close'].values.reshape(-1,1))

    # Split the data into training and testing sets
    training_size = int(len(scaled_data) * 0.7)
    testing_size = len(scaled_data) - training_size
    train_data = scaled_data[0:training_size,:]
    test_data = scaled_data[training_size:len(scaled_data),:]

    # Create the dataset for the LSTM model
    def create_dataset(dataset, time_step=1):
        dataX, dataY = [], []
        for i in range(len(dataset)-time_step-1):
            a = dataset[i:(i+time_step), 0]
            dataX.append(a)
            dataY.append(dataset[i + time_step, 0])
        return np.array(dataX), np.array(dataY)

    # Set the time step and reshape the data for the LSTM model
    time_step = 50
    X_train, y_train = create_dataset(train_data, time_step)
    X_test, y_test = create_dataset(test_data, time_step)
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

    # Build the LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(LSTM(50, return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')

    # Train the model
    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=64, verbose=0)

    # Make predictions on the testing data
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)

    # Create buy, sell, or hold signals based on predicted prices
    signal = get_signal(predictions)
    last_signal = signal[-1]

    return last_signal

