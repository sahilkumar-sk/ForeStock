from api_handler import get_stock_data

# Test the function with a stock ticker (e.g., AAPL for Apple)
data = get_stock_data('AAPL', '1mo')
print(data)
