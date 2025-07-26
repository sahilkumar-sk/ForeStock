import io
import pandas as pd
import numpy as np
from keras.models import load_model
from api_handler import get_stock_data
from utils.preprocessing import preprocess_data_with_sentiment, prepare_data
import tensorflow as tf
from datetime import date, timedelta

# Load the model once when the app starts
model = load_model('stock_prediction_model_with_tuned_hyperparameters.keras')

def get_predicted_prices(stock_symbol, prediction_days=[1, 15, 30], download_csv=False):
    try:
        if stock_symbol is None:
            raise ValueError("Stock symbol cannot be None")

        print(f"Predicting price for stock: {stock_symbol}")

        # Fetch and preprocess data
        df_test = get_stock_data(stock_symbol, '5y')
        if df_test is None or df_test.empty:
            raise ValueError(f"No data fetched for stock symbol: {stock_symbol}")

        df_test_scaled, scaler = preprocess_data_with_sentiment(
            df_test, stock_symbol, api_key='6033221f384f4e4395d7410df82c3fdd'
        )
        X_test, _ = prepare_data(df_test_scaled, time_step=60)

        # Predict multiple days
        def predict_multiple_days(model, X_test, days):
            predicted_prices = []
            input_seq = X_test[-1, :, :]
            for _ in range(days):
                pred = model.predict(input_seq.reshape(1, *input_seq.shape))
                predicted_prices.append(pred[0, 0])
                input_seq = np.roll(input_seq, -1, axis=0)
                input_seq[-1, 0] = pred
            return np.array(predicted_prices)

        predictions = {}
        for days in prediction_days:
            raw = predict_multiple_days(model, X_test, days)
            reshaped = raw.reshape(-1, 1)
            num_feats = scaler.n_features_in_
            to_inverse = np.concatenate(
                [reshaped, np.zeros((reshaped.shape[0], num_feats - 1))],
                axis=1
            )
            inv = scaler.inverse_transform(to_inverse)[:, 0]
            predictions[days] = inv.tolist()

        # If download_csv is True, generate a CSV of the next 30 trading days only
        if download_csv:
            today = date.today()
            pointer = today
            rows = []
            for price in predictions[30]:
                # advance to next business day
                pointer += timedelta(days=1)
                while pointer.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                    pointer += timedelta(days=1)
                rows.append({
                    "Date": pointer.isoformat(),
                    "Predicted Price": price
                })

            df = pd.DataFrame(rows)
            csv_file = io.BytesIO()
            df.to_csv(csv_file, index=False)
            csv_file.seek(0)
            return csv_file

        # Otherwise, return the raw predictions dict
        for days in prediction_days:
            print(f"Predicted price for next {days} day(s): {predictions[days][-1]}")
        return predictions

    except Exception as e:
        print(f"Error in get_predicted_prices: {e}")
        raise ValueError(f"Error predicting stock price for {stock_symbol}: {e}")
