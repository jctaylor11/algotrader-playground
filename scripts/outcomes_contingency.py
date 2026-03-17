"""
Script to compute and visualise a contingency table showing which threshold is hit before the other.

For each candle, it compares which return threshold was hit first in a threshold pair (for all pairs), and counts the occurrence for each. 
Ultimately, it displays "How many outcomes hit X (row threshold) before Y (column threshold)".

Since it is computed simultaneously in long format, the results are pivoted to a matrix format, to be displayed as a heatmap.

This is useful to calculate conditional probabilities for each outcome threshold pair, which can be used to compute an expected value given a market state (e.g indicator values). 
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text

from src.data.database import get_engine

conn = get_engine()

# Period limit for outcome to resolve - handled as unresolved if X or Y thresholds do not hit
holding_period = 1400000

query = """
    WITH candle_count AS (
        SELECT
            COUNT (DISTINCT candle_id) AS total_candles
        FROM OUTCOMES
    )
    SELECT
        a.return_threshold AS threshold_a,
        b.return_threshold AS threshold_b,
        COUNT(*) AS count_x_before_y,
        total_candles
    FROM outcomes a
    JOIN outcomes b ON a.candle_id = b.candle_id AND (a.return_threshold * b.return_threshold < 0)
    CROSS JOIN candle_count
    WHERE (a.candles_to_hit < b.candles_to_hit
        OR (a.candles_to_hit IS NOT NULL AND b.candles_to_hit IS NULL)) 
        AND a.candles_to_hit <= :holding_period
    GROUP BY threshold_a, threshold_b, total_candles
    ORDER BY threshold_a;
"""

outcomes_df = pd.read_sql(text(query), conn, params={"holding_period": holding_period})

# Calculate probabilities from contingency values using total_candles as denominator
total_candles = outcomes_df['total_candles'][0]
outcomes_df['probability'] = outcomes_df['count_x_before_y'] / total_candles

# The df is in long format, and therefore pivoted to create a contingency table to count values where row threshold is hit by colum threshold
contingency_table = outcomes_df.pivot_table(index='threshold_a', columns='threshold_b', values='probability')

# Seaborn to plot the contingency table
plt.figure(figsize=(12, 8))
ax = sns.heatmap(contingency_table, annot=True, cmap="viridis")

ax.invert_yaxis()
plt.title(f"P(X before Y) and resolved within {holding_period} periods")
plt.show()