from sqlalchemy import text
import pandas as pd

from src.data.database import get_engine, populate_candles

engine = get_engine()

# Define inputs
pair = "BTCUSDT"
interval = "1h"
start = "2021-11-01"
end = "2025-01-01"

populate_candles(pair, interval, start, end, engine)