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

    df = get_binance_ohlcv(symbol, interval, start)

    filename = f"{symbol}_{interval}_{start}"

    df.to_csv(f"src/data/ohlcv/{filename}.csv", index=True)


save_binance_ohlcv('BTCUSDT', '1h')

