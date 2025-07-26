# test_get_predicted_price.py
from test_model import get_predicted_price

ticker = "AAPL"
try:
    predicted_price = get_predicted_price(ticker)
    print(f"Predicted price for {ticker}: {predicted_price}")
except Exception as e:
    print(f"Error: {e}")