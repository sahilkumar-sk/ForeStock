import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from utils.preprocessing import add_technical_indicators, preprocess_data_with_sentiment, prepare_data
from fetch_news import get_daily_sentiment

def test_add_technical_indicators():
    # Mock dataset
    data = {
        'Close': [100, 101, 102, 103, 104]
    }
    df = pd.DataFrame(data)
    
    # Test function
    df_with_indicators = add_technical_indicators(df)
    
    # Assertions
    assert '50_day_MA' in df_with_indicators.columns
    assert 'RSI' in df_with_indicators.columns
    assert 'MACD' in df_with_indicators.columns

@patch('utils.preprocessing.fetch_news')
@patch('utils.preprocessing.get_daily_sentiment')
def test_preprocess_data_with_sentiment(mock_get_daily_sentiment, mock_fetch_news):
    # Mock dataset
    data = {
        'Open': [100, 101, 102],
        'High': [105, 106, 107],
        'Low': [95, 96, 97],
        'Close': [102, 103, 104],
        'Volume': [1000, 1100, 1200]
    }
    df = pd.DataFrame(data, index=pd.date_range(start='2023-01-01', periods=3))
    
    # Mock API key and stock symbol
    api_key = "mock_api_key"
    stock_symbol = "AAPL"
    
    # Mock external dependencies
    mock_fetch_news.return_value = [
        {"title": "Stock prices are rising today.", "publishedAt": "2023-01-01T10:00:00Z"},
        {"title": "The market is experiencing a downturn.", "publishedAt": "2023-01-02T10:00:00Z"}
    ]
    mock_get_daily_sentiment.return_value = 0.5

    # Test function
    df_scaled, scaler = preprocess_data_with_sentiment(df, stock_symbol, api_key)
    
    # Assertions
    assert df_scaled is not None
    assert len(df_scaled) == len(df)

def test_prepare_data():
    # Mock scaled data
    df_scaled = np.array([[i] * 10 for i in range(100)])
    
    # Test function
    X, y = prepare_data(df_scaled, time_step=10)
    
    # Assertions
    assert X.shape[0] == len(df_scaled) - 10
    assert X.shape[1] == 10
    assert y.shape[0] == len(df_scaled) - 10

def test_get_daily_sentiment():
    # Mock articles
    articles = [
        {"title": "Stock prices are rising today."},  # Positive sentiment
        {"title": "The market is experiencing a downturn."},  # Negative sentiment
        {"title": "Investors are optimistic about the future."}  # Positive sentiment
    ]
    
    # Test function
    avg_sentiment = get_daily_sentiment(articles)
    
    # Assertions
    assert avg_sentiment != 0  # Ensure sentiment is calculated
    assert -1 <= avg_sentiment <= 1  # Sentiment should be in the range [-1, 1]