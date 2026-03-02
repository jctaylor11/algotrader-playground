from sqlalchemy import text

from src.data.database import get_engine


def main(): 
    engine = get_engine()

    with engine.begin() as conn:
        print("Connected")

        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS pair_lookup (
                          id SERIAL PRIMARY KEY,
                          coin_pair text);
                    """))
        
        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS interval_lookup (
                          id SERIAL PRIMARY KEY,
                          interval_name text UNIQUE);
                    """))

        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS candles (
                          id SERIAL PRIMARY KEY, 
                          open_timestamp timestamptz,
                          pair_id integer REFERENCES pair_lookup(id),
                          interval_id integer REFERENCES interval_lookup(id), 
                          open_price numeric,
                          high numeric,
                          low numeric,
                          close numeric,
                          volume numeric,
                          UNIQUE (open_timestamp, pair_id, interval_id));
                    """))3
        
        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS outcomes (
                          id SERIAL PRIMARY KEY,
                          candle_id integer REFERENCES candles(id),
                          return_threshold numeric,
                          candles_to_hit integer,
                          UNIQUE (candle_id, return_threshold));
                    """))
        
        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS indicator_lookup (
                          id SERIAL PRIMARY KEY,
                          indicator_name text);
                    """))
        
        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS indicator_values (
                          id SERIAL PRIMARY KEY,
                          candle_id integer REFERENCES candles(id),
                          indicator_id integer REFERENCES indicator_lookup(id),
                          indicator_value numeric,
                          UNIQUE (candle_id, indicator_id));
                    """))


if __name__ == "__main__":
    main()