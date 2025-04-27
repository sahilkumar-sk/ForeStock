import io
import pandas as pd
import numpy as np
from keras.models import load_model
from api_handler import get_stock_data  # If this is still needed for some data, otherwise it can be removed
from utils.preprocessing import preprocess_data_with_sentiment, prepare_data
import tensorflow as tf

# Load the model once when the app starts
model = load_model('stock_prediction_model_with_tuned_hyperparameters.keras')  # Load the model globally

def get_predicted_prices(stock_symbol, prediction_days=[1, 15, 30], download_csv=False):
    try:
        if stock_symbol is None:
            raise ValueError("Stock symbol cannot be None")  # Ensure stock_symbol is provided

        print(f"Predicting price for stock: {stock_symbol}")

        # Fetch stock data - If you no longer need this, you can comment/remove this code.
        print("Fetching stock data...")
        df_test = get_stock_data(stock_symbol, '5y')
        if df_test is None or df_test.empty:
            raise ValueError(f"No data fetched for stock symbol: {stock_symbol}")

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
                input_sequence = np.roll(input_sequence, shift=-1, axis=0)
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

        # If download_csv is True, create the CSV file
        if download_csv:
            # Generate a DataFrame from the predictions
            data = []
            for days in prediction_days:
                for price in predictions[days]:
                    data.append({"Prediction": f"Next {days} Days", "Price": price})

            df = pd.DataFrame(data)

            # Create an in-memory CSV file
            csv_file = io.BytesIO()
            df.to_csv(csv_file, index=False)
            csv_file.seek(0)  # Reset the pointer to the start of the file

            # Return the CSV file (Flask will use this to send the file as download)
            return csv_file  # Flask will send this file to the client for download

        # If CSV is not requested, just return the predictions
        for days in prediction_days:
            print(f"Predicted price for next {days} day(s): {predictions[days][-1]}")

        return predictions  # Returns predictions as a dictionary with lists

    except Exception as e:
        print(f"Error in get_predicted_prices: {e}")
        raise ValueError(f"Error predicting stock price for {stock_symbol}: {e}")
