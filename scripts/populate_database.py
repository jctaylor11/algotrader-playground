from sqlalchemy import text
import pandas as pd

from src.data.database import get_engine, populate_candles, populate_outcomes

engine = get_engine()

# Define inputs
pair = "BTCUSDT"
interval = "1h"
start = "2021-01-01"
end = "2023-01-01"

threshold = 1.05    # For returns in outcomes table

populate_candles(pair, interval, start, end, engine)
populate_outcomes(engine, threshold)
