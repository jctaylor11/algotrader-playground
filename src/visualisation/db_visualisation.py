from sqlalchemy import text
import pandas as pd

def view_outcomes_wide(engine):
    """
    SQL query that pivots the outcomes table into wide format for easy interpretation, joined onto candles.
    This is useful for manually understanding and sense checking the data.
    """
    with engine.begin() as conn:
        cursor = conn.execute(text("""
            SELECT 
                candles.id,
                candles.open_timestamp,
                candles.high,
                MAX(CASE WHEN o.return_threshold = 0.90 THEN o.candles_to_hit END) AS "hit_0.90",
                MAX(CASE WHEN o.return_threshold = 0.91 THEN o.candles_to_hit END) AS "hit_0.91",
                MAX(CASE WHEN o.return_threshold = 0.92 THEN o.candles_to_hit END) AS "hit_0.92",
                MAX(CASE WHEN o.return_threshold = 0.93 THEN o.candles_to_hit END) AS "hit_0.93",
                MAX(CASE WHEN o.return_threshold = 0.94 THEN o.candles_to_hit END) AS "hit_0.94",
                MAX(CASE WHEN o.return_threshold = 0.95 THEN o.candles_to_hit END) AS "hit_0.95",
                MAX(CASE WHEN o.return_threshold = 0.96 THEN o.candles_to_hit END) AS "hit_0.96",
                MAX(CASE WHEN o.return_threshold = 0.97 THEN o.candles_to_hit END) AS "hit_0.97",
                MAX(CASE WHEN o.return_threshold = 0.98 THEN o.candles_to_hit END) AS "hit_0.98",
                MAX(CASE WHEN o.return_threshold = 0.99 THEN o.candles_to_hit END) AS "hit_0.99",
                MAX(CASE WHEN o.return_threshold = 1.01 THEN o.candles_to_hit END) AS "hit_1.01",
                MAX(CASE WHEN o.return_threshold = 1.02 THEN o.candles_to_hit END) AS "hit_1.02",
                MAX(CASE WHEN o.return_threshold = 1.03 THEN o.candles_to_hit END) AS "hit_1.03",
                MAX(CASE WHEN o.return_threshold = 1.04 THEN o.candles_to_hit END) AS "hit_1.04",
                MAX(CASE WHEN o.return_threshold = 1.05 THEN o.candles_to_hit END) AS "hit_1.05",
                MAX(CASE WHEN o.return_threshold = 1.06 THEN o.candles_to_hit END) AS "hit_1.06",
                MAX(CASE WHEN o.return_threshold = 1.07 THEN o.candles_to_hit END) AS "hit_1.07",
                MAX(CASE WHEN o.return_threshold = 1.08 THEN o.candles_to_hit END) AS "hit_1.08",
                MAX(CASE WHEN o.return_threshold = 1.09 THEN o.candles_to_hit END) AS "hit_1.09",
                MAX(CASE WHEN o.return_threshold = 1.10 THEN o.candles_to_hit END) AS "hit_1.10"
            FROM candles
            JOIN outcomes AS o ON candles.id = o.candle_id
            GROUP BY candles.id, candles.open_timestamp, candles.high;                          
        """))

        # Saving to dataframe to visualise in IDE
        outcomes_wide = pd.DataFrame(cursor.fetchall(), columns=cursor.keys())

        return outcomes_wide 