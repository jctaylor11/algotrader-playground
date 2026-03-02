import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from src.data.historical_data import fetch_binance_ohlcv_all, clean_ohlcv_data


def get_engine():
    load_dotenv()

    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME')
    port = os.getenv('DB_PORT')

    try:
        # From sqlalchemy docs: database url = dialect+driver://username:password@host:port/database
        engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to database: {e}")
        
    return engine


def populate_candles(pair, interval, start, end, engine):
    # Fetch and clean data from Binance
    candles_df_raw = fetch_binance_ohlcv_all(pair, interval, start, end)
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
        pair_id = conn.execute(text("SELECT id FROM pair_lookup WHERE coin_pair = :symbol;"), {"symbol": pair}).scalar()
        if pair_id is None: 
            pair_id = conn.execute(text("INSERT INTO pair_lookup (coin_pair) VALUES (:symbol) RETURNING id"), {"symbol": pair}).scalar()

        # Add pair id and interval id foreign keys to candles df
        candles_df["pair_id"] = pair_id
        candles_df["interval_id"] = interval_id

        # Insert candles df to postgres
        candles_df.to_sql('candles', conn, if_exists='append', index=False)

