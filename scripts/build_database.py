from sqlalchemy import text

from src.data.database import get_engine


def main(): 
    engine = get_engine()

    with engine.begin() as conn:
        print("Connected")

        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS pair_lookup (
                          id SERIAL PRIMARY KEY,
                          coin_pair text)
                    """))
        
        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS interval_lookup (
                          id SERIAL PRIMARY KEY,
                          interval_name text)
                    """))

        conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ohlcv (
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
                    """))


if __name__ == "__main__":
    main()