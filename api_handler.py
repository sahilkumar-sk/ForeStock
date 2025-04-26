import yfinance as yf

def get_stock_data(stock_symbol, period='1d'):
    try:
        if not stock_symbol:
            raise ValueError("Ticker is empty.")
        
        # Fetch stock data using yfinance
        stock_data = yf.Ticker(stock_symbol)
        stock_history = stock_data.history(period=period)  # Fetch data for the specified period
        
        if stock_history.empty:
            raise ValueError(f"No data found for ticker: {stock_symbol}")
        
        return stock_history  # Return the stock history

    except Exception as e:
        raise ValueError(f"Error fetching stock data for {stock_symbol}: {e}")
