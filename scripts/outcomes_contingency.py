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

from src.data.database import get_engine

conn = get_engine()

query = """
    SELECT
        a.return_threshold AS threshold_x,
        b.return_threshold AS threshold_y,
        COUNT(*) AS count_x_before_y
    FROM outcomes a
    JOIN outcomes b ON a.candle_id = b.candle_id
        AND a.return_threshold < b.return_threshold
    WHERE a.candles_to_hit < b.candles_to_hit
    GROUP BY threshold_x, threshold_y
    ORDER BY threshold_x;
"""

df = pd.read_sql(query, conn)

# The df is in long format, and therefore pivoted to create a contingency table to count values where row threshold is hit by colum threshold
contingency_table = df.pivot_table(index='threshold_x', columns='threshold_y', values='count_x_before_y')

# Seaborn to plot the contingency table
plt.figure(figsize=(12, 8))
sns.heatmap(contingency_table)
plt.show()