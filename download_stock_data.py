from pandas_datareader import data as pdr
import datetime
import pandas as pd
import os
from config import stock_symbols

# ─── CONFIG ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── FUNCTION TO DOWNLOAD DATA ─────────────────────────────────────────────────
def download_stock_data(symbol: str, years: int = 3):
    """
    Download historical stock data for the past `years` years using Stooq.
    Saves it as a CSV file under /data.
    """
    end = datetime.datetime.today()
    start = end - datetime.timedelta(days=365 * years)

    try:
        df = pdr.DataReader(symbol, 'stooq', start, end)
        df = df.sort_index()
        if df.empty:
            raise ValueError("No data returned.")
        file_path = os.path.join(OUTPUT_DIR, f"{symbol.upper()}_3y.csv")
        df.to_csv(file_path)
        print(f"✅ Saved {symbol} data to {file_path}")
    except Exception as e:
        print(f"❌ Failed to fetch {symbol}: {e}")

# ─── MAIN RUNNER ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for symbol in stock_symbols:
        download_stock_data(symbol)
