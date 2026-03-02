from sqlalchemy import text
import pandas as pd

from src.data.database import get_engine
from src.data.historical_data import fetch_binance_ohlcv_all, clean_ohlcv_data

engine = get_engine()

# Define inputs
symbol = "BTCUSDT"
interval = "12h"
start = "2024-11-01"
end = "2025-01-01"

# Fetch and clean data from Binance
candles_df_raw = fetch_binance_ohlcv_all(symbol, interval, start, end)
candles_df = clean_ohlcv_data(candles_df_raw)

# Map df columns to sql column names 
candles_df.reset_index(inplace=True)
candles_df.rename(columns={
    "date": "open_timestamp",
    "open": "open_price",
    }, inplace=True)

with engine.begin() as conn: 
    # Get or create interval id in lookup table
    interval_id = conn.execute(text("SELECT id FROM interval_lookup WHERE interval_name = :interval;"), {"interval": interval}).scalar()
    if interval_id is None: 
        interval_id = conn.execute(text("INSERT INTO interval_lookup (interval_name) VALUES (:interval) RETURNING id"), {"interval": interval}).scalar()

    # Get or create pair id in lookup table
    pair_id = conn.execute(text("SELECT id FROM pair_lookup WHERE coin_pair = :symbol;"), {"symbol": symbol}).scalar()
    if pair_id is None: 
        pair_id = conn.execute(text("INSERT INTO pair_lookup (coin_pair) VALUES (:symbol) RETURNING id"), {"symbol": symbol}).scalar()

    # Add pair id and interval id foreign keys to candles df
    candles_df["pair_id"] = pair_id
    candles_df["interval_id"] = interval_id

    # Insert candles df to postgres
    candles_df.to_sql('candles', conn, if_exists='append', index=False)