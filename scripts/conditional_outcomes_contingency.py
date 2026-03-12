import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text

from src.data.database import get_engine

conn = get_engine()

number_of_bins = 10     # For discretisation of indicator values by percentile
holding_period = 14     # Period limit for outcome to resolve - handled as unresolved if X or Y thresholds do not hit

query = """
    WITH indicator_binned AS (
        SELECT                              -- Discretises the indicators values into bins of specified number
            candle_id,
            indicator_id,
            NTILE(:number_of_bins) OVER (PARTITION BY indicator_id ORDER BY indicator_value) AS percentile_bin
        FROM indicator_values              
        WHERE candle_id IN (SELECT candle_id) FROM outcomes)
    ),
    indicator_binned_counts AS (            -- CTE for count of candles in each bin, only for pandas to pull through in one database request
        SELECT                              -- (ie it's not used in the core logic)
            indicator_id,
            percentile_bin,
            COUNT(*) AS bin_candle_count
        FROM indicator_binned
        GROUP BY indicator_id, percentile_bin
    )
    SELECT
        a.return_threshold AS threshold_x,
        b.return_threshold AS threshold_y,
        ib.indicator_id,
        ib.percentile_bin,
        COUNT(*) AS x_hit_before_y,
        ibc.bin_candle_count
    FROM outcomes a
    JOIN indicator_binned ib 
        ON ib.candle_id = a.candle_id
    JOIN outcomes b 
        ON b.candle_id = a.candle_id 
        AND (a.return_threshold * b.return_threshold < 0)
    JOIN indicator_binned_counts ibc 
        ON ibc.percentile_bin = ib.percentile_bin 
        AND ibc.indicator_id = ib.indicator_id
    WHERE 
        (a.candles_to_hit < b.candles_to_hit 
        OR (a.candles_to_hit IS NOT NULL AND b.candles_to_hit IS NULL))
        AND a.candles_to_hit <= :holding_period
    GROUP BY 
        threshold_x, 
        threshold_y, 
        ib.indicator_id, 
        ib.percentile_bin, 
        ibc.bin_candle_count
    ORDER BY threshold_x;
"""

raw_conditional_x_before_y= pd.read_sql(text(query), conn, params={"number_of_bins": number_of_bins, "holding_period": holding_period})

print(raw_conditional_x_before_y)

