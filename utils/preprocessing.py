import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from sklearn.preprocessing import StandardScaler  # Import StandardScaler for sentiment
from fetch_news import fetch_news, get_daily_sentiment
from ta.momentum import RSIIndicator  # RSI calculation from TA-Lib
from datetime import datetime

def add_technical_indicators(df):
    """
    Add Moving Averages, RSI, MACD, and EMA to the stock data.
    
    Parameters:
    df (pd.DataFrame): Stock data with 'Close' prices.
    
    Returns:
    pd.DataFrame: Stock data with additional technical features.
    """
    # Calculate moving averages
    df['50_day_MA'] = df['Close'].rolling(window=50).mean()  # 50-day moving average
    df['200_day_MA'] = df['Close'].rolling(window=200).mean()  # 200-day moving average
    
    # Calculate RSI
    rsi_indicator = RSIIndicator(df['Close'], window=14)
    df['RSI'] = rsi_indicator.rsi()
    
    # Calculate MACD (Moving Average Convergence Divergence)
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()  # Short-term EMA
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()  # Long-term EMA
    df['MACD'] = df['EMA_12'] - df['EMA_26']  # MACD line
    
    # Calculate EMA (Exponential Moving Average)
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()  # 50-day EMA
    
    return df


def preprocess_data_with_sentiment(df, stock_symbol, api_key):
    # Fetch news articles related to the stock symbol
    articles = fetch_news(stock_symbol, api_key)
    
    # Get sentiment scores for each day
    sentiment_scores = []
    for date in df.index:
        articles_on_date = [
            article for article in articles
            if article.get('publishedAt', '').startswith(str(date.date()))
        ]
        sentiment_score = get_daily_sentiment(articles_on_date)
        sentiment_scores.append(sentiment_score if sentiment_score is not None else 0)
    
    # Add sentiment scores as a new column
    df['Sentiment'] = sentiment_scores

    # Add technical indicators
    df = add_technical_indicators(df)
    
    # Handle missing data
    df.ffill(inplace=True)  # Forward fill
    df.bfill(inplace=True)  # Backward fill

    # Scale the data
    stock_scaler = MinMaxScaler(feature_range=(0, 1))
    sentiment_scaler = StandardScaler()
    df_scaled_stock = stock_scaler.fit_transform(df[['Open', 'High', 'Low', 'Close', 'Volume', '50_day_MA', '200_day_MA', 'RSI', 'MACD', 'EMA_50']])
    sentiment_scaled = sentiment_scaler.fit_transform(df[['Sentiment']])
    df_scaled = np.concatenate((df_scaled_stock, sentiment_scaled), axis=1)

    return df_scaled, stock_scaler

def prepare_data(df_scaled, time_step=60):
    """
    Prepare data for LSTM by creating sequences of time steps.
    
    Parameters:
    df_scaled (np.array): The scaled stock data (including sentiment).
    time_step (int): The number of previous days used to predict the next day's stock price.
    
    Returns:
    X, y: The feature set and target variable for training.
    """
    X, y = [], []
    
    # Ensure there are enough rows to create sequences of 'time_step'
    if len(df_scaled) <= time_step:
        raise ValueError(f"Data is too short. Length of data must be greater than {time_step}.")
    
    for i in range(time_step, len(df_scaled)):
        X.append(df_scaled[i-time_step:i, :])  # Use multiple columns as features
        y.append(df_scaled[i, 3])  # The next day's 'Close' price as the target (index 3 is 'Close')
    
    X = np.array(X)
    y = np.array(y)
    
    # Reshape X to be 3D (samples, time steps, features) for LSTM
    X = np.reshape(X, (X.shape[0], X.shape[1], X.shape[2]))  # Ensure the shape is correct
    
    return X, y
