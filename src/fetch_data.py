from dotenv import load_dotenv
import os
from binance.client import Client
import pandas as pd

# Load Binance API keys from .env
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("SECRET_KEY")

client = Client(api_key, api_secret, tld = "com")

def get_history(symbol, interval, start, end=None): 

    # Get historical market data from API client and save to dataframe
    bars = client.get_historical_klines(symbol, interval, start, end)
    df = pd.DataFrame(bars)

    df["Date"] = pd.to_datetime(df.loc[:,0], unit="ms")
    df.columns = ["Open Time", "Open", "High", "Low", "Close", "Volume",
                  "Close Time", "Quote Asset Volume", "Number of Trades",
                  "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore", "Date"]
    
    # Filter the df to the columns I want and set the date as the index
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    df.set_index("Date", inplace=True)

    # Pandas defaults to object type, so we convert columns to numeric, verified with df.dtypes
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


