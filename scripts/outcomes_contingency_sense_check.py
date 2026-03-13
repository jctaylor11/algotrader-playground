"""
This sense check helps understand how each candle is being accounted for in the contingency analysis, and see they are
being accounted for in a mutually exclusive and collectively exhaustive way.

There are four groups:
A - X is hit before Y 
B - Y is hit before X
C - Neither X or Y is hit in the sample period (unresolved)
D - X and Y are both hit in the same candle (indistinguishable)

If they have all been accounted for, the matrix will show all values as (total candles / bins).
Adding more bins will increase the number of NaNs, since the granularity increases likelihood that the count for that threshold pair
in the given bin will be 0, which gets omitted from the dataframe, resulting in NaN. 
"""


import pandas as pd
from sqlalchemy import text

from src.data.database import get_engine

number_of_bins = 10
holding_period = 1000
indicator_id = 1
percentile_bin = 1

def get_conditional_sql(base_query, condition, number_of_bins, holding_period):
    query = base_query.format(filter=condition)

    # Pull from SQL and filter for relevant indicator ID and bin
    df = pd.read_sql(text(query), conn, params={"number_of_bins": number_of_bins, "holding_period": holding_period})
    df = df.loc[(df['indicator_id'] == indicator_id) & (df['percentile_bin'] == percentile_bin)]
    return df

conn = get_engine()

base_query = """
    WITH indicator_binned AS (
        SELECT                              -- Discretises the indicators values into bins of specified number
            candle_id,
            indicator_id,
            NTILE(:number_of_bins) OVER (PARTITION BY indicator_id ORDER BY indicator_value) AS percentile_bin
        FROM indicator_values            
        WHERE candle_id IN (SELECT candle_id FROM outcomes)
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
        {filter}
    GROUP BY 
        threshold_x, 
        threshold_y, 
        ib.indicator_id, 
        ib.percentile_bin, 
        ibc.bin_candle_count
    ORDER BY threshold_x;
"""

## x hit before y
x_before_y_condition = """
    (a.candles_to_hit < b.candles_to_hit 
    OR (a.candles_to_hit IS NOT NULL AND b.candles_to_hit IS NULL))
    AND a.candles_to_hit <= :holding_period
"""

unresolved_condition = """
    (a.candles_to_hit IS NULL OR a.candles_to_hit > :holding_period)
    AND (b.candles_to_hit IS NULL OR b.candles_to_hit > :holding_period)
"""

same_candle_condition = """
    a.candles_to_hit = b.candles_to_hit
"""

x_before_y = get_conditional_sql(base_query, x_before_y_condition, number_of_bins, holding_period)
unresolved = get_conditional_sql(base_query, unresolved_condition, number_of_bins, holding_period)
indistinguishable = get_conditional_sql(base_query, same_candle_condition,  number_of_bins, holding_period)

x_before_y_contingency = x_before_y.pivot_table(index='threshold_x', columns='threshold_y', values='x_hit_before_y')
unresolved_contingency = unresolved.pivot_table(index='threshold_x', columns='threshold_y', values='x_hit_before_y').reindex_like(x_before_y_contingency).fillna(0)
indistinguishable_contingency = indistinguishable.pivot_table(index='threshold_x', columns='threshold_y', values='x_hit_before_y').reindex_like(x_before_y_contingency).fillna(0)
y_before_x_contingency = x_before_y_contingency.T

element_wise_sum = x_before_y_contingency + unresolved_contingency + indistinguishable_contingency + y_before_x_contingency

print(element_wise_sum)

