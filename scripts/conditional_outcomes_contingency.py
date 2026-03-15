import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import seaborn as sns
from sqlalchemy import text

from src.data.database import get_engine

conn = get_engine()

number_of_bins = 10     # For discretisation of indicator values by percentile
holding_period = 1000     # Period limit for outcome to resolve - handled as unresolved if X or Y thresholds do not hit

query = """
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

df_raw = pd.read_sql(text(query), conn, params={"number_of_bins": number_of_bins, "holding_period": holding_period})

df_raw['probability'] = df_raw['x_hit_before_y'] / df_raw['bin_candle_count']

## Single plot view
fig, ax = plt.subplots(figsize=(12,8))

indicator_id = 1
percentile_bin = 5
df_bin = df_raw.loc[(df_raw['indicator_id'] == indicator_id) & (df_raw['percentile_bin'] == percentile_bin)]   # Filter for bin
df_contingency = df_bin.pivot_table(values='probability', index='threshold_x', columns='threshold_y')

sns.heatmap(df_contingency, ax=ax, cmap='viridis')
fig.suptitle(f"Probability of X before Y, Percentile Bin {percentile_bin}", fontsize=24)
ax.set_xticklabels([f"{x*100:.0f}%" for x in df_contingency.columns])
ax.set_yticklabels([f"{y*100:.0f}%" for y in df_contingency.index])
ax.invert_yaxis()
plt.show()

## All bin subplots view
fig, axs = plt.subplots(3,4,figsize=(16, 9))
axs = axs.flatten()     # To make it iterable

# To ensure all subplots have the same scale for visual comparison
p_min = df_raw['probability'].min()
p_max = df_raw['probability'].max()

# Iterates through each bin and adds as subplot
total_bins = df_raw['percentile_bin'].unique()
for percentile_bin in total_bins:
    df_bin = df_raw.loc[(df_raw['indicator_id'] == 1) & (df_raw['percentile_bin'] == percentile_bin)] 
    df_contingency = df_bin.pivot_table(values='probability', index='threshold_x', columns='threshold_y')
    sns.heatmap(df_contingency, ax=axs[percentile_bin-1], cmap='viridis', vmin=p_min, vmax=p_max, cbar=False)
    axs[percentile_bin-1].invert_yaxis()
    axs[percentile_bin-1].set_title(f"Percentile Bin {percentile_bin}")

# Plot and colour bar spacings
fig.subplots_adjust(left=0.05, right=0.85, top=0.92, bottom=0.12, hspace=0.6, wspace=0.4)   
cbar_ax = fig.add_axes([0.9, 0.12, 0.02, 0.78])  # [left, bottom, width, height]

# One colour bar normalised by the global min and max probabilities
fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(p_min, p_max), cmap='viridis'), cax=cbar_ax, label='Probability')
fig.suptitle("Probability X Before Y, All Percentile Bins")
plt.show()

## All heatmaps on one
df_multi_contingency = df_raw.pivot_table(values='probability', index='threshold_x', columns=['percentile_bin', 'threshold_y'])   # Multi column index

fig, axs = plt.subplots(figsize=(16, 9))
sns.heatmap(df_multi_contingency, cmap='viridis')
axs.invert_yaxis()
fig.suptitle("Probability X Before Y, All Percentile Bins Multi-Index")
plt.show()

