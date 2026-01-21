from dotenv import load_dotenv
import os
from binance.client import Client
import pandas as pd
import time
from datetime import datetime

# Load Binance API keys from .env
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("SECRET_KEY")

# Initialise Binance client (API wrapper binance-python) 
client = Client(api_key, api_secret, tld = "com")


def get_binance_ohlcv(symbol, interval, start, end=None):
    """Fetch and clean historical OHLCV data from Binance using python-binance wrapper"""
    bars = client.get_historical_klines(symbol, interval, start, end, limit=1000)

    # Returns empty dataframe if it didn't get a response
    if not bars:
        return pd.DataFrame()

    time.sleep(0.3)     # To ensure it doesn't violate Binance's API rate limits 
    df = pd.DataFrame(bars)
                      
    df.columns = ["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"]

    df["Date"] = pd.to_datetime(df["Open time"], unit='ms')
    df.set_index("Date", inplace = True)

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors = "coerce")

    return df

def save_binance_ohlcv(symbol, interval, start=None):
    """
    Save historical ohlcv. If no start is defined, entire history will be saved. 
    Can also be downloaded from https://data.binance.vision/?prefix=data/ to reduce API traffic
    """
    if (start == None):
        earliest_timestamp = client._get_earliest_valid_timestamp(symbol, interval)
        start = datetime.fromtimestamp(earliest_timestamp / 1000).strftime("%Y-%m-%d")   # Formating for filename

    original_start = start
    data_chunks = []
    while True: 
        
        data_chunk = get_binance_ohlcv(symbol, interval, start)

        if data_chunk.empty:
            # It's taken up to latest date
            break
        else: 
            data_chunks.append(data_chunk)

        latest_timestamp = data_chunk.index.max()
        start = latest_timestamp + pd.Timedelta(interval)       # Advancing time cursor to avoid duplicates
        start = start.strftime("%Y-%m-%d")                      # Convert to string as required by get_binance_ohlcv 

        print(f"Start: {start}")

    # Logic to concat list of dfs and save to csv
    df_to_save = pd.concat(data_chunks)

    # Remove any duplicates
    duplicates = df_to_save.index.duplicated()
    df_to_save = df_to_save[~duplicates]
    print(f"Duplicates removed: {duplicates.sum()}. (Should be 0 - non-zero suggests logic error)")

    df_to_save.to_csv(f"data/raw_ohlcv/{symbol}-{interval}-{original_start}.csv", index=True)



save_binance_ohlcv('BTCUSDT', '1d')


