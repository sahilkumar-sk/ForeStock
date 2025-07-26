import yfinance as yf
import pandas as pd
from flask import Flask, render_template, jsonify, request, send_file
from keras.models import load_model  # Importing keras to load the model
from test_model import get_predicted_prices  # Import the prediction function from test_model.py
from fetch_news import fetch_news  # Import the function from fetch_news.py
import requests
import io
import datetime
from operator import itemgetter

from operator import itemgetter
from chatbot import generate_reply


app = Flask(__name__)



def fetch_stock_market_news(api_key):
    today = datetime.datetime.now()
    from_date = (today - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')

    url = f"https://newsapi.org/v2/everything?q=stock market&from={from_date}&to={today_str}&sortBy=publishedAt&language=en&pageSize=10&apiKey={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        return []  # Fallback to empty list

    articles = []
    if news_data.get('status') == 'ok':
        for article in news_data['articles']:
            articles.append({
                "title": article.get('title') or "Untitled",
                "url": article.get('url') or "#",
                "urlToImage": article.get('urlToImage')  # Keep it None if missing
            })

    return articles



def remove_duplicates(articles):
    seen = set()
    unique_articles = []
    for article in articles:
        identifier = (article.get('title', '').strip(), article.get('url', '').strip())
        if identifier not in seen:
            seen.add(identifier)
            unique_articles.append(article)
    return unique_articles



def get_trending_stocks():
    trending_tickers = ["AAPL", "TSLA", "AMZN", "MSFT", "GOOGL"]  # You can customize this list
    trending_stocks = []

    for ticker in trending_tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")  # Last 2 days
            if len(hist) >= 2:
                yesterday_close = hist['Close'].iloc[-2]
                today_close = hist['Close'].iloc[-1]
                change_percent = ((today_close - yesterday_close) / yesterday_close) * 100
                trending_stocks.append({
                    "symbol": ticker,
                    "price": f"${today_close:.2f}",
                    "change_percent": change_percent
                })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

    return trending_stocks
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
    
    # Prepare the data for CSV
    data = {
        "Prediction": ["Next 1 Day"] + ["Next 15 Days"] * len(predictions_15_days) + ["Next 30 Days"] * len(predictions_30_days),
        "Price": [predictions_1_day[0]] + predictions_15_days + predictions_30_days
    }
    df = pd.DataFrame(data)
    
    # Create an in-memory file using BytesIO
    csv_file = io.BytesIO()
    df.to_csv(csv_file, index=False)
    csv_file.seek(0)  # Reset pointer to the start of the file
    
    return csv_file

@app.route('/')
def home():
    trending_stocks = get_trending_stocks()

    api_key = "6033221f384f4e4395d7410df82c3fdd"
    articles = fetch_stock_market_news(api_key)
    articles = remove_duplicates(articles)

    print(f"Total articles fetched: {len(articles)}")  # Safe debug

    return render_template('index.html', trending_stocks=trending_stocks, articles=articles)

@app.route('/chatbot', methods=['POST'])
def chatbot_route():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"reply": "Please enter a message."})

    try:
        response = generate_reply(user_input)
        return jsonify({"reply": response})
    except Exception as e:
        print(f"[Chatbot Route Error] {e}")
        return jsonify({"reply": "Something went wrong. Please try again later."})

@app.route('/predictions', methods=['GET', 'POST'])
def predictions():
    if request.method == 'POST':
        ticker = request.form.get("ticker")  # Get ticker from form input
        if not ticker:
            print("Error: No ticker provided")
            return render_template('predictions.html', error="No ticker provided.")
        print(f"Ticker received: {ticker}")  # Log the ticker value to verify        
        try:
            # Call the get_predicted_prices function and pass ticker
            predictions = get_predicted_prices(ticker, prediction_days=[1, 15, 30], download_csv=True)

            # If CSV is requested, return it
            if isinstance(predictions, io.BytesIO):  # If the return value is the CSV file (in-memory)
                return send_file(predictions, as_attachment=True, download_name=f"{ticker}_predictions.csv", mimetype="text/csv")

            # If CSV is not requested, render the predictions
            return render_template(
                'predictions.html',
                ticker=ticker,
                predictions_1_day=predictions[1],
                predictions_15_days=predictions[15],
                predictions_30_days=predictions[30]
            )
        except Exception as e:
            print(f"Error: {e}")
            return render_template('predictions.html', error=f"Error generating predictions: {e}")
    else:
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
    api_key = "6033221f384f4e4395d7410df82c3fdd"  # Replace with your actual API key
    stock_symbol = request.args.get('stock', 'stock market')  # Default to "stock market" if no stock is specified
    
    # Fetch news articles
    articles = fetch_news(stock_symbol, api_key)

    # Remove duplicate articles
    articles = remove_duplicates(articles)

    # Filter out articles without a description
    articles = [article for article in articles if article.get('description')]

    # Sort articles by published date (assuming 'publishedAt' is in the article data)
    articles = sorted(articles, key=itemgetter('publishedAt'), reverse=True)  # Sorting in descending order

    # Pass articles to the template
    return render_template('news.html', articles=articles)

@app.route('/trends')
def trends():
    return render_template('trends.html')  # This renders 'trends.html' from the templates folder

if __name__ == '__main__':
    app.run(debug=True)
