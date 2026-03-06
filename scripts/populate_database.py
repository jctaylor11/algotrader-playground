from sqlalchemy import text

from src.data.database import get_engine, populate_candles, populate_outcomes, populate_indicator_rsi

REBUILD_CANDLES = False
REBUILD_OUTCOMES = False
REBUILD_RSI_INDICATOR = True

# Define inputs
pair = "BTCUSDT"
interval = "1h"
start = "2021-01-01"
end = "2023-01-01"

# Custom thresholds ranging from -10% to +10%. Threshold flexibility is accommodated by long format of outcomes schema
thresholds = [i / 100 for i in range(-10, 11) if i != 10]

engine = get_engine()

if REBUILD_CANDLES:
    populate_candles(pair, interval, start, end, engine)

if REBUILD_OUTCOMES:
    for threshold in thresholds:
        populate_outcomes(engine, threshold)

if REBUILD_RSI_INDICATOR:
    populate_indicator_rsi(engine)