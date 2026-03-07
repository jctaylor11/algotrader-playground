from sqlalchemy import text

from src.data.database import get_engine


def main(): 
    engine = get_engine()

    with engine.begin() as conn:
        print("Connected")

        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS pair_lookup (
                          id SERIAL PRIMARY KEY,
                          coin_pair text NOT NULL);
                    """))
        
        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS interval_lookup (
                          id SERIAL PRIMARY KEY,
                          interval_name text NOT NULL UNIQUE);
                    """))

        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS candles (
                          id SERIAL PRIMARY KEY, 
                          open_timestamp timestamptz NOT NULL,
                          pair_id integer NOT NULL REFERENCES pair_lookup(id),
                          interval_id integer NOT NULL REFERENCES interval_lookup(id), 
                          open_price numeric NOT NULL,
                          high_price numeric NOT NULL,
                          low_price numeric NOT NULL,
                          close_price numeric NOT NULL,
                          volume numeric NOT NULL,
                          UNIQUE (open_timestamp, pair_id, interval_id));
                    """))
        
        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS outcomes (
                          id SERIAL PRIMARY KEY,
                          candle_id integer NOT NULL REFERENCES candles(id),
                          return_threshold numeric NOT NULL,
                          candles_to_hit integer,           -- null indicates threshold never hit
                          UNIQUE (candle_id, return_threshold));
                    """))
        
        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS indicator_lookup (
                          id SERIAL PRIMARY KEY,
                          indicator_name text NOT NULL);
                    """))
        
        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS indicator_values (
                          id SERIAL PRIMARY KEY,
                          candle_id integer NOT NULL REFERENCES candles(id),
                          indicator_id integer NOT NULL REFERENCES indicator_lookup(id),
                          indicator_value numeric,     -- Can be null if insufficient periods
                          UNIQUE (candle_id, indicator_id));
                    """))


if __name__ == "__main__":
    main()