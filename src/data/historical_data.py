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

    complete = False
    new_start_time = start
    while not complete: 
        
        if start == new_start_time:     # To initialise df if it's the first iteration
            df = get_binance_ohlcv(symbol, interval, start)
        else:
            df = pd.concat([df, get_binance_ohlcv(symbol, interval, new_start_time)])

        # Get the a latest time
        latest_time = df.index.max()
        print(f"Saved until: {latest_time}")

        new_start_time = (latest_time + pd.Timedelta(interval))

        todays_date = pd.Timestamp.now().normalize()
        if new_start_time >= todays_date:
            complete = True
        else:
            new_start_time = new_start_time.strftime("%Y-%m-%d %H:%M:%S")     # String format so it can be parsed by get_binance_ohlcv function

    # Remove any duplicates just to make sure - Though there shouldn't be any considering the pd.Timedelta(interval)
    duplicates = df.index.duplicated()
    df = df[~duplicates]
    print(f"Duplicates removed: {df[duplicates]}. (Should be an empty list - non-empty suggests logic error)")

    # Saving the data to csv
    filename = f"{symbol}_{interval}_{start}"
    df.to_csv(f"data/raw_ohlcv/{filename}.csv", index=True)



save_binance_ohlcv('BTCUSDT', '1w')


