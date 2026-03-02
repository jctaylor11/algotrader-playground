from dotenv import load_dotenv
import os
from binance.client import Client
import pandas as pd
import time
from datetime import datetime
import streamlit as st
import math

# Initialise Binance client (API wrapper binance-python) 
client = Client(tld = "com")


def fetch_custom_binance_ohlcv(symbol, interval, start, end, _progress_cb=None):
    """
    Fetches and cleans custom ohlcv data from Binance, as requested by user in Streamlit app.py.
    Return Pandas dataframe.
    """
    custom_data = fetch_binance_ohlcv_all(symbol, interval, start, end, _progress_cb)

    custom_data = clean_ohlcv_data(custom_data) 

    return custom_data


def save_binance_ohlcv(symbol, interval, start=None, end=None):
    """
    Save historical ohlcv. If start and end are None, entire history will be saved. 
    Returns the filepath for immediately use. 
    Can also be downloaded from https://data.binance.vision/?prefix=data/ to reduce API traffic
    """
    # If start isnot specified, starts from earliest available timestamp
    if start is None:
        earliest_timestamp = client._get_earliest_valid_timestamp(symbol, interval)
        start = datetime.fromtimestamp(earliest_timestamp / 1000).strftime("%Y-%m-%d")   # Formating for filename

    if end is None: 
        end = datetime.now().strftime("%Y-%m-%d")
        
    # Iteratively pulls all the data in batches from Binance to save as csv
    df_to_save = fetch_binance_ohlcv_all(symbol, interval, start, end)

    df_to_save = clean_ohlcv_data(df_to_save)

    filepath = f"data/raw_ohlcv/{symbol}-{interval}-{start}.csv"
    df_to_save.to_csv(filepath, index=True)

    return filepath


def fetch_binance_ohlcv_all(symbol, interval, start, end, progress_cb=None):
    latest_timestamp = None

    # If start is earlier than earliest start, start = earliest start
    earliest_timestamp_unix = client._get_earliest_valid_timestamp(symbol, interval)
    earliest_timestamp = pd.to_datetime(earliest_timestamp_unix, unit='ms')
    if pd.to_datetime(start) < earliest_timestamp:
        start = earliest_timestamp.strftime("%Y-%m-%d")

    # For Streamlit's progress tracking loading bar
    data_batches = []
    batch_count = 0
    total_batches = math.ceil((pd.Timestamp(end) - pd.Timestamp(start)) / pd.to_timedelta(interval) / 1000)

    while True: 
        print(f"Pulling batch: {start}")

        data_batch = _fetch_binance_ohlcv_batch(symbol, interval, start, end)

        if data_batch.empty or latest_timestamp == data_batch.index.max():          # Second condition prevents infinite loop at boundary
            break               # Pulled all data up to today's date
        
        # Handles progress tracking, and sends progress back to UI via progress_cb callback function
        if progress_cb:
            batch_count += 1
            current_progress = int((batch_count / total_batches) * 100)
            progress_cb(current_progress)
            
        data_batches.append(data_batch)

        # Advances time cursor to avoid duplicates
        latest_timestamp = data_batch.index.max()
        start = str(latest_timestamp + pd.Timedelta(interval))      
        
    # Logic to concat list of dfs and save to csv
    all_fetched_data = pd.concat(data_batches)

    return all_fetched_data


def _fetch_binance_ohlcv_batch(symbol, interval, start, end=None):
    """Fetch historical OHLCV data from Binance using python-binance wrapper, up to maximum request size (1000 bars)"""
    bars = client.get_historical_klines(symbol, interval, start, end, limit=1000)

    # Returns empty dataframe if it didn't get a response
    if not bars:
        return pd.DataFrame()

    time.sleep(0.3)     # To ensure it doesn't violate Binance's API rate limits 
    df = pd.DataFrame(bars)
                      
    df = _format_ohlcv_data(df)

    return df


def _format_ohlcv_data(df):
    df.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "num_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"]

    df["date"] = pd.to_datetime(df["open_time"], unit='ms')
    df.set_index("date", inplace = True)

    df = df[["open", "high", "low", "close", "volume"]].copy()

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors = "coerce")

    return df


def clean_ohlcv_data(df):
    # Remove any duplicates
    duplicates = df.index.duplicated()
    df = df[~duplicates]
    print(f"Duplicates removed: {duplicates.sum()}. (Should be 0 - non-zero suggests logic error)")

    return df


def fetch_min_volume_tickers(min_volume):
    """
    Returns all tickers quoted in USDT with a 24hr USDT volume greater than the min_volume argument.
    Sorted alphabetically. 
    """
    try:
        all_tickers_data = client.get_ticker()
    except Exception as e:
        print(f"Failed to fetch tickers: {e}")
        return []

    tickers = []
    for ticker in all_tickers_data:
        if ticker['symbol'][-4:] == 'USDT' and float(ticker['quoteVolume']) > min_volume:
            tickers.append(ticker['symbol'])
    
    tickers.sort()
    return tickers



# Required since Streamlit-decorated functions will break if called from outside of Streamlit
# This will decorate the function only if running in Streamlit context
# Inner function (_fetch_binance_ohlcv_batch) cached instead of outer (fetch_custom_binance_ohlcv) due to callback function compatibility with st.cache_data
try:
    _fetch_binance_ohlcv_batch = st.cache_data(show_spinner=False)(_fetch_binance_ohlcv_batch)
except RuntimeError:
    print("Not called from Streamlit - not applying cache")


# For testing
if __name__ == "__main__":
    filepath = save_binance_ohlcv('BTCUSDT', '8h', start="2024-01-01", end="2025-01-01")
    # print(filepath)

    # df = fetch_custom_binance_ohlcv('BTCUSDT', '4h', start='2025-01-01', end='2025-05-05')
    # print(df)
