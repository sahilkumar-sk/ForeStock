from keras.models import load_model
from api_handler import get_stock_data
from utils.preprocessing import preprocess_data_with_sentiment, prepare_data
import numpy as np
import pandas as pd
from datetime import timedelta
import pandas_market_calendars as mcal
import tensorflow as tf

def get_predicted_prices(stock_symbol, prediction_days=[1, 15, 30]):
    try:
        print(f"Predicting price for stock: {stock_symbol}")

        # Load the trained model
        print("Loading model...")
        model = load_model('stock_prediction_model_with_tuned_hyperparameters.keras')

        # Fetch stock data
        print("Fetching stock data...")
        df_test = get_stock_data(stock_symbol, '5y')
        print(f"Fetched data shape: {df_test.shape}")

        # Preprocess the test data
        print("Preprocessing data...")
        df_test_scaled, scaler = preprocess_data_with_sentiment(df_test, stock_symbol, api_key='6033221f384f4e4395d7410df82c3fdd')

        # Prepare the test data
        print("Preparing data for prediction...")
        X_test, _ = prepare_data(df_test_scaled, time_step=60)
        print(f"Shape of X_test: {X_test.shape}")

        # Function to predict multiple days
        def predict_multiple_days(model, X_test, days):
            predicted_prices = []
            input_sequence = X_test[-1, :, :]  # Start with the last data point

            for day in range(days):
                # Predict the next price for this day
                predicted_price = model.predict(input_sequence.reshape(1, input_sequence.shape[0], input_sequence.shape[1]))  # Predict the next price
                predicted_prices.append(predicted_price[0, 0])

                # Update the input sequence for the next prediction
                # Roll the input sequence to move it forward by 1 time step
                input_sequence = np.roll(input_sequence, shift=-1, axis=0)
                # Replace the last feature (last time step) with the predicted price
                input_sequence[-1, 0] = predicted_price  # Replace the first feature with the predicted value

            return np.array(predicted_prices)  # Return the array of predicted prices for multiple days

        # Predict stock prices for the specified days (1, 15, 30)
        print("Making predictions for the next 1, 15, and 30 days...")
        predictions = {}
        for days in prediction_days:
            predicted_stock_price = predict_multiple_days(model, X_test, days)

            # Reshape and inverse transform predictions
            predicted_stock_price_reshaped = np.reshape(predicted_stock_price, (predicted_stock_price.shape[0], 1))
            num_features = scaler.n_features_in_

            predicted_stock_price_with_all_columns = np.concatenate(
                (predicted_stock_price_reshaped, np.zeros((predicted_stock_price_reshaped.shape[0], num_features - 1))),
                axis=1
            )
            predicted_stock_price = scaler.inverse_transform(predicted_stock_price_with_all_columns)[:, 0]

            predictions[days] = predicted_stock_price.tolist()  # Convert NumPy array to list

        # Return the predictions for 1, 15, and 30 days
        for days in prediction_days:
            print(f"Predicted price for next {days} day(s): {predictions[days][-1]}")

        return predictions  # Returns predictions as a dictionary with lists

    except Exception as e:
        print(f"Error in get_predicted_prices: {e}")
        raise ValueError(f"Error predicting stock price for {stock_symbol}: {e}")
