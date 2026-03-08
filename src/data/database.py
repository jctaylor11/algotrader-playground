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
        "high": "high_price",
        "low": "low_price",
        "close": "close_price"
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


def populate_outcomes(engine, threshold):
    """
    Populates the number of candles passed from the starting candle before it first hits the given return threshold.  
    Assumes candle IDs are in order of date and contiguously stored. 
    """
    with engine.begin() as conn: 
        if threshold > 0: 
            join_condition = "b.high_price > a.close_price * (1 + :threshold)"
        else:
            join_condition = "b.low_price < a.close_price * (1 + :threshold)"

        # LEFT JOIN used so applies to each parent candle, rather than silently dropping
        conn.execute(text(f"""
            INSERT INTO outcomes (candle_id, return_threshold, candles_to_hit)
            SELECT 
                a.id AS candle_id,
                :threshold AS return_threshold,
                MIN(b.id) - a.id AS candles_to_hit
            FROM candles a
            LEFT JOIN candles b ON b.id > a.id AND {join_condition}
            GROUP BY a.id, a.high_price
            LIMIT 1000
            ON CONFLICT (candle_id, return_threshold) DO UPDATE
                SET candles_to_hit = EXCLUDED.candles_to_hit
        """), {"threshold": threshold})

    
def populate_indicator_rsi(engine):
    with engine.begin() as conn:
        rsi_period = 14     # 14 is standard RSI period
        indicator_id = get_or_create_lookup(conn, "indicator_lookup", "indicator_name", "rsi")

        conn.execute(text("""
            WITH deltas AS (            -- CTE for difference with prior period
                SELECT 
                    id AS candle_id,
                    open_timestamp,
                    pair_id,
                    interval_id,
                    close_price - LAG(close_price) OVER (PARTITION BY pair_id, interval_id ORDER BY open_timestamp) AS delta 	-- Parition by pair_id and interval_id since they define a unique candle
                FROM candles
            ),
            gain_losses AS (            -- CTE to separate the gains from the losses 
                SELECT 
                    *, 
                    GREATEST(delta, 0) AS gain,
                    GREATEST(-delta, 0) AS loss
                FROM deltas
            ),
            rsi AS (                    -- CTE for RSI calculation
                SELECT
                    *,
                    100 - (100.0 / (1 + 
                        AVG(gain) OVER (PARTITION BY pair_id, interval_id ORDER BY open_timestamp ROWS BETWEEN (:rsi_period - 1) PRECEDING AND CURRENT ROW) / 
                        NULLIF (AVG(loss) OVER (PARTITION BY pair_id, interval_id ORDER BY open_timestamp ROWS BETWEEN (:rsi_period - 1) PRECEDING AND CURRENT ROW), 0))) AS rsi_value,        -- NULIF required to avoid division by zero
                    ROW_NUMBER() OVER (PARTITION BY pair_id, interval_id ORDER BY open_timestamp) AS row_num		                                                            -- Assigns row number so we can filter for >= 14 
                FROM gain_losses
            )
            INSERT INTO indicator_values (candle_id, indicator_id, indicator_value)
            SELECT
                candle_id,
                :indicator_id,
                rsi_value
            FROM rsi
            WHERE row_num > (:rsi_period - 1)
            ;"""), {"indicator_id": indicator_id, "rsi_period": rsi_period})


def get_or_create_lookup(conn, table, column, value):
    row_id = conn.execute(text(f"SELECT id FROM {table} WHERE {column} = :symbol;"), {"symbol": value}).scalar()
    if row_id is None: 
        row_id = conn.execute(text(f"INSERT INTO {table} ({column}) VALUES (:symbol) RETURNING id"), {"symbol": value}).scalar()
    
    return row_id
