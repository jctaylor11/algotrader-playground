import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text

from src.data.database import get_engine

conn = get_engine()

number_of_bins = 10     # For discretisation of indicator values by percentile
holding_period = 20     # Period limit for outcome to resolve - handled as unresolved if A or B thresholds do not hit

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
        a.return_threshold AS threshold_a,
        b.return_threshold AS threshold_b,
        ib.indicator_id,
        ib.percentile_bin,
        COUNT(*) AS a_hit_before_b,
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
        threshold_a, 
        threshold_b, 
        ib.indicator_id, 
        ib.percentile_bin, 
        ibc.bin_candle_count
    ORDER BY threshold_a;
"""

df_raw = pd.read_sql(text(query), conn, params={"number_of_bins": number_of_bins, "holding_period": holding_period})

df_raw['probability'] = df_raw['a_hit_before_b'] / df_raw['bin_candle_count']

## Single plot view
fig, ax = plt.subplots(figsize=(12,8))

indicator_id = 1
percentile_bin = 1
df_bin = df_raw.loc[(df_raw['indicator_id'] == indicator_id) & (df_raw['percentile_bin'] == percentile_bin)]   # Filter for bin
df_contingency = df_bin.pivot_table(values='probability', index='threshold_a', columns='threshold_b')

sns.heatmap(df_contingency, ax=ax, cmap='viridis')
fig.suptitle(f"Probability of Threshold A before Threshold B\nIndicator ID {indicator_id}, Percentile Bin {percentile_bin}", fontsize=24)
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

# Filter for indicator
df_raw_ind = df_raw[df_raw['indicator_id'] == indicator_id]

# Iterates through each bin and adds as subplot
total_bins = df_raw_ind['percentile_bin'].unique()
for i, p_bin in enumerate(sorted(total_bins)):               # TODO: should be filtered for indicator id outside of the loop 
    df_bin = df_raw_ind.loc[(df_raw['percentile_bin'] == p_bin)] 
    df_contingency = df_bin.pivot_table(values='probability', index='threshold_a', columns='threshold_b')
    sns.heatmap(df_contingency, ax=axs[i], cmap='viridis', vmin=p_min, vmax=p_max, cbar=False)
    axs[i].invert_yaxis()
    axs[i].set_title(f"Percentile Bin {p_bin}")

# Plot and colour bar spacings
fig.subplots_adjust(left=0.06, right=0.89, top=0.85, bottom=0.11, hspace=0.6, wspace=0.4)   
cbar_ax = fig.add_axes([0.93, 0.12, 0.02, 0.78])  # [left, bottom, width, height]

# One colour bar normalised by the global min and max probabilities
fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(p_min, p_max), cmap='viridis'), cax=cbar_ax, label='Probability')
fig.suptitle(f"Probability of Threshold A Before Threshold B\nIndicator ID {indicator_id}, All Percentile Bins", fontsize=24)
plt.show()

## All heatmaps on one
df_multi_contingency = df_raw.pivot_table(values='probability', index='threshold_a', columns=['percentile_bin', 'threshold_b'])   # Multi column index

fig, axs = plt.subplots(figsize=(16, 9))
sns.heatmap(df_multi_contingency, cmap='viridis')
axs.invert_yaxis()
fig.suptitle(f"Probability of Threshold A Before Threshold B\nIndicator ID {indicator_id}, All Percentile Bins Multi-Index", fontsize=24)
plt.show()

## Single EV plot
# Self join to retrieve P(B before A) by flipping the index on P(A before B)
df_ev_merged = df_raw.merge(df_raw, left_on=['threshold_a', 'threshold_b', 'percentile_bin', 'indicator_id'], right_on=['threshold_b', 'threshold_a', 'percentile_bin', 'indicator_id'], suffixes=['_A', '_B'])
df_ev_merged['ev'] = abs(df_ev_merged['threshold_a_A']) * df_ev_merged['probability_A'] + (-abs(df_ev_merged['threshold_b_A']) * df_ev_merged['probability_B'])

# Filter for bin and indicator to display
df_ev_bin = df_ev_merged.loc[(df_ev_merged['indicator_id'] == indicator_id) & (df_ev_merged['percentile_bin'] == percentile_bin)].copy()   # Filter for bin
ev_contingency = df_ev_bin.pivot_table(values='ev', index='threshold_a_A', columns='threshold_b_A')

# Plot heatmap
fig, ax = plt.subplots(figsize=(12,8))
sns.heatmap(ev_contingency, cmap='RdBu', center=0)
ax.invert_yaxis()
ax.set_ylabel("Take Profit")
ax.set_xlabel("Stop Loss")
fig.suptitle(f"Expected Value for Take-Profit/Stop-Loss Setup\nFor Indicator ID {indicator_id} in Percentile Bin {percentile_bin}", fontsize=24)
plt.show()

## Subplots
fig, axs = plt.subplots(3,4,figsize=(16, 9))
axs = axs.flatten()     # To make it iterable

# Filter for indicator
df_ev_merged = df_ev_merged.loc[df_ev_merged['indicator_id'] == indicator_id].copy()

# Get extreme values for colour bar
ev_max = df_ev_merged['ev'].max()
ev_min = df_ev_merged['ev'].min()

# Loop through each bin and add to the plot
total_bins = df_ev_merged['percentile_bin'].unique()
for i, p_bin in enumerate(sorted(total_bins)): 
    df_ev_bin = df_ev_merged.loc[df_ev_merged['percentile_bin'] == p_bin]
    ev_contingency = df_ev_bin.pivot_table(values='ev', index='threshold_a_A', columns='threshold_b_A')
    sns.heatmap(ev_contingency, ax=axs[i], cmap='RdBu', vmin=ev_min, vmax=ev_max, cbar=False)

    axs[i].invert_yaxis()
    axs[i].set_title(f"Percentile Bin {p_bin}")

    axs[i].set_ylabel("Take Profit")
    axs[i].set_xlabel("Stop Loss")

# Plot and colour bar spacings
fig.subplots_adjust(left=0.06, right=0.89, top=0.85, bottom=0.11, hspace=0.6, wspace=0.4)   
cbar_ax = fig.add_axes([0.93, 0.12, 0.02, 0.78])  # [left, bottom, width, height]

# One colour bar normalised by the global min and max probabilities
fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(ev_min, ev_max), cmap='RdBu'), cax=cbar_ax, label='EV')
fig.suptitle(f"Expected Value for Take-Profit/Stop-Loss Setup\nIndicator ID {indicator_id}, All Percentile Bins", fontsize=24)
plt.show()


