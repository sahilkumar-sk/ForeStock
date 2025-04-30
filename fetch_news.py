import requests
from textblob import TextBlob
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)

# Fetch news data from NewsAPI with retries
def fetch_news(stock_symbol, api_key):
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={api_key}"
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    try:
        response = session.get(url)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        if not articles:
            logging.warning(f"No articles found for {stock_symbol}.")
        return articles
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news for {stock_symbol}: {e}")
        return []

# Perform sentiment analysis using TextBlob
def get_sentiment(article_text):
    """
    Get the sentiment polarity of a given text using TextBlob.
    Polarity ranges from -1 (negative) to 1 (positive).
    """
    if not article_text.strip():  # Handle empty or whitespace-only text
        return 0  # Neutral sentiment
    blob = TextBlob(article_text)
    return blob.sentiment.polarity

# Get average sentiment for a list of articles
def get_daily_sentiment(articles):
    """
    Calculate the average sentiment score for a list of articles.

    Parameters:
    articles (list): List of articles, where each article is a dictionary 
                     containing a 'title' key.

    Returns:
    float: Average sentiment score for the articles.
    """
    sentiment_scores = [
        get_sentiment(article.get('title', '')) for article in articles if article.get('title')
    ]
    if sentiment_scores:
        return sum(sentiment_scores) / len(sentiment_scores)
    else:
        return 0  # No articles available

# Test block to allow user input
if __name__ == "__main__":
    # Replace with your actual API key
    api_key = "6033221f384f4e4395d7410df82c3fdd"  # Replace with your NewsAPI key
    
    # Get stock name from the user
    stock_symbol = input("Enter the stock name or symbol: ").strip()
    
    # Fetch news articles
    articles = fetch_news(stock_symbol, api_key)
    
    # Print the fetched articles
    if articles:
        print(f"\n{'='*80}")
        print(f"Fetched {len(articles)} articles for '{stock_symbol}':")
        print(f"{'='*80}")
        print(f"{'Title':<60} | {'Published Date':<20}")
        print(f"{'-'*80}")
        for article in articles[:5]:  # Display only the first 5 articles
            title = article.get('title', 'No Title')[:57] + "..." if len(article.get('title', '')) > 60 else article.get('title', 'No Title')
            published_at = article.get('publishedAt', 'No Publish Date')
            print(f"{title:<60} | {published_at:<20}")
        print(f"{'='*80}")
        
        # Calculate and print the average sentiment
        avg_sentiment = get_daily_sentiment(articles)
        print(f"\nAverage Sentiment Score for '{stock_symbol}': {avg_sentiment:.2f}")
        print(f"{'='*80}")
    else:
        print(f"\nNo articles found for '{stock_symbol}'.")