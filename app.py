import yfinance as yf
import pandas as pd
from flask import Flask, render_template, jsonify, request, send_file
from keras.models import load_model  # Importing keras to load the model
from test_model import get_predicted_prices  # Import the prediction function from test_model.py
from fetch_news import fetch_news  # Import the function from fetch_news.py

app = Flask(__name__)

# Load the model once when the app starts
model = None
try:
    print("Loading model...")
    model = load_model('stock_prediction_model_with_tuned_hyperparameters.keras')  # Loading model here
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

# Function to generate CSV for stock predictions
def generate_predictions_csv(ticker, predictions_1_day, predictions_15_days, predictions_30_days):
    if not predictions_1_day or not predictions_15_days or not predictions_30_days:
        raise ValueError(f"No predictions available for ticker: {ticker}")
    
    # Create a DataFrame with predictions
    data = {
        "Prediction": ["Next 1 Day"] + ["Next 15 Days"] * len(predictions_15_days) + ["Next 30 Days"] * len(predictions_30_days),
        "Price": [predictions_1_day[0]] + predictions_15_days + predictions_30_days
    }
    df = pd.DataFrame(data)
    
    # Save the DataFrame to a CSV file
    csv_file = f"{ticker}_predictions.csv"
    df.to_csv(csv_file, index=False)
    
    return csv_file

@app.route('/')
def home():
    return render_template('index.html')  # Renders 'index.html'

@app.route('/predictions', methods=['GET', 'POST'])
def predictions():
    if request.method == 'POST':
        ticker = request.form.get("ticker")  # Get ticker from form input
        print(f"Ticker received: {ticker}")  # Debug print to check ticker
        if not ticker:
            return render_template('predictions.html', ticker=None, predictions_1_day=None, predictions_15_days=None, predictions_30_days=None)

        # Generate predictions for 1, 15, and 30 days using the imported function from test_model.py
        predictions = get_predicted_prices(ticker, prediction_days=[1, 15, 30])

        predictions_1_day = predictions.get(1, [])
        predictions_15_days = predictions.get(15, [])
        predictions_30_days = predictions.get(30, [])

        # Handle CSV download button
        if request.form.get("download_csv"):
            print(f"Generating CSV for ticker: {ticker}")  # Debug print to check ticker again
            # Generate CSV and send it as a downloadable file
            csv_file = generate_predictions_csv(ticker, predictions_1_day, predictions_15_days, predictions_30_days)
            return send_file(csv_file, as_attachment=True)

        # Pass predictions to the template
        return render_template(
            'predictions.html',
            ticker=ticker,
            predictions_1_day=predictions_1_day,
            predictions_15_days=predictions_15_days,
            predictions_30_days=predictions_30_days
        )
    else:
        # Handle GET request (when the user clicks the "Predictions" link)
        return render_template('predictions.html', ticker=None, predictions_1_day=None, predictions_15_days=None, predictions_30_days=None)

@app.route('/api/predict', methods=['POST'])
def predict_api():
    if request.method == 'POST':
        ticker = request.json.get("ticker")  # Get ticker from request body
        if not ticker:
            return jsonify({'error': 'Ticker is required'}), 400

        try:
            # Fetch current stock price using yfinance
            stock_data = yf.Ticker(ticker)
            stock_history = stock_data.history(period='1d')
            
            if stock_history.empty:
                return jsonify({'error': f'No data found for ticker: {ticker}'}), 400

            stock_price = stock_history['Close'].iloc[0]  # Get today's closing price

            # Get predicted stock prices
            predictions = get_predicted_prices(ticker, prediction_days=[1, 15, 30])

            predictions['current_price'] = round(stock_price, 2)
            predictions = {str(key): value for key, value in predictions.items()}

            return jsonify(predictions)  # Return predictions as JSON

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return jsonify({'error': f'An error occurred while fetching data for {ticker}.'}), 500

@app.route('/news')
def news():
    # Replace with your actual API key
    api_key = "6033221f384f4e4395d7410df82c3fdd"
    stock_symbol = request.args.get('stock', 'stock market')  # Default to "stock market" if no stock is specified

    # Fetch news articles
    articles = fetch_news(stock_symbol, api_key)

    # Pass articles to the template
    return render_template('news.html', articles=articles)

@app.route('/trends')
def trends():
    return render_template('trends.html')  # This renders 'trends.html' from the templates folder

if __name__ == '__main__':
    app.run(debug=True)
