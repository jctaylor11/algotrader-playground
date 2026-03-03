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
        # Get or create interval id and pair id in lookup table
        pair_id = get_or_create_lookup(conn, "pair_lookup", "coin_pair", pair)
        interval_id = get_or_create_lookup(conn, "interval_lookup", "interval_name", interval)


        # Add pair id and interval id foreign keys to candles df
        candles_df["pair_id"] = pair_id
        candles_df["interval_id"] = interval_id

        # Insert candles df to postgres
        candles_df.to_sql('candles', conn, if_exists='append', index=False)


def get_or_create_lookup(conn, table, column, value):
    row_id = conn.execute(text(f"SELECT id FROM {table} WHERE {column} = :symbol;"), {"symbol": value}).scalar()
    if row_id is None: 
        row_id = conn.execute(text(f"INSERT INTO {table} ({column}) VALUES (:symbol) RETURNING id"), {"symbol": value}).scalar()
    
    return row_id
