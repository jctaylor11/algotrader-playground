from sqlalchemy import text

from src.data.database import get_engine, populate_candles, populate_outcomes

REBUILD_CANDLES = False

# Define inputs
pair = "BTCUSDT"
interval = "1h"
start = "2021-01-01"
end = "2023-01-01"

thresholds = [i / 100 for i in range(90, 111) if i != 100]

engine = get_engine()

if REBUILD_CANDLES:
    populate_candles(pair, interval, start, end, engine)

for threshold in thresholds:
    populate_outcomes(engine, threshold)

