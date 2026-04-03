"""
Script to compute all EV heatmap for a single indicator
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import text

from src.data.database import get_engine


def fetch_data(number_of_bins, holding_period):
    """
    Returns a DataFrame with columns: candle_id, indicator_id, percentile_bin,
    threshold_a, threshold_b, a_hit_before_b, bin_candle_count.
    """
    conn = get_engine()
 
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

    # Pandas pulls sql via sqlalchemy and calculates probability P(A before B), for each threshold pair, for each bin
    df_raw = pd.read_sql(text(query), conn, params={"number_of_bins": number_of_bins, "holding_period": holding_period})
    return df_raw


def get_bin_probability_contingency(df_outcomes, percentile_bin):
    """Returns probability contingency pivot table for the specified bin."""
    df_bin = df_outcomes.loc[df_outcomes['percentile_bin'] == percentile_bin]   # Filter for bin
    single_bin_contingency = df_bin.pivot_table(values='probability', index='threshold_a', columns='threshold_b')

    return single_bin_contingency


def get_bin_ev_contingency(df_outcomes, percentile_bin):
    """
    Returns EV contingency for the specified bin.
    """
    # Self join to retrieve P(B before A) by flipping the index on P(A before B)
    df_ev_merged = df_outcomes.merge(df_outcomes,
        left_on=['threshold_a', 'threshold_b', 'percentile_bin'],       
        right_on=['threshold_b', 'threshold_a', 'percentile_bin'], 
        suffixes=['_A', '_B']
    )
    df_ev_merged['ev'] = abs(df_ev_merged['threshold_a_A']) * df_ev_merged['probability_A'] + (-abs(df_ev_merged['threshold_b_A']) * df_ev_merged['probability_B'])

    # Filter for bin and indicator to display
    df_ev_bin = df_ev_merged.loc[df_ev_merged['percentile_bin'] == percentile_bin].copy()   # Filter for bin
    ev_contingency = df_ev_bin.pivot_table(values='ev', index='threshold_a_A', columns='threshold_b_A')

    return ev_contingency


def plot_heatmap(contingency, colour, title, center=None):
    """Returns a heatmap figure for a single contingency."""
    fig, ax = plt.subplots(figsize=(12,8))
    sns.heatmap(contingency, ax=ax, cmap=colour, center=center)
    fig.suptitle(title, fontsize=24)

    ax.set_ylabel("Take Profit")
    ax.set_xlabel("Stop Loss")    
    ax.set_xticklabels([f"{i*100:.0f}%" for i in contingency.columns])
    ax.set_yticklabels([f"{i*100:.0f}%" for i in contingency.index])
    ax.invert_yaxis()

    return fig


def plot_multi_heatmap(contingency, colour, title):
    """Returns a heatmap figure for a multi-index contingency across all bins."""
    fig, ax = plt.subplots(figsize=(16, 9))
    sns.heatmap(contingency, ax=ax, cmap=colour)
    fig.suptitle(title, fontsize=24)
    ax.set_ylabel("Take Profit")
    ax.set_xlabel("Stop Loss")  
    ax.invert_yaxis()

    return fig


def get_all_bin_contingencies(df_outcomes, contingency_function):
    """Agnostic to probability of ev contingencies"""
    all_bin_contingencies = {}      # Stores contingencies by their percentile bin number

    total_bins = df_outcomes['percentile_bin'].unique()
    for bin_num in sorted(total_bins):        
        bin_contingency = contingency_function(df_outcomes, bin_num)
        all_bin_contingencies[bin_num] = bin_contingency

    return all_bin_contingencies


# Function to plot all contingnecies on one figure
def plot_all_heatmaps(contingencies, label, colour, title): 
    """Returns the figure of all bin probability suplots"""
    fig, axs = plt.subplots(3,4,figsize=(16, 9))        # TODO: Make this dynamic to number of subplots
    axs = axs.flatten()     # To make it iterable

    # To ensure all subplots have the same scale for visual comparison
    p_min = min(np.nanmin(c.values) for c in contingencies.values())    # Finds min 
    p_max = max(np.nanmax(c.values) for c in contingencies.values()) 

    # Iterate through each contingency to add it to axs
    for i, (bin_num, contingency) in enumerate(contingencies.items()):
        sns.heatmap(contingency, ax=axs[i], cmap=colour, vmin=p_min, vmax=p_max, cbar=False)
        axs[i].set_title(f"Percentile Bin {bin_num}")
        axs[i].set_ylabel("Take Profit")
        axs[i].set_xlabel("Stop Loss")
        axs[i].invert_yaxis()    

    # Plot and colour bar spacings
    fig.subplots_adjust(left=0.06, right=0.89, top=0.85, bottom=0.11, hspace=0.6, wspace=0.4)   
    cbar_ax = fig.add_axes([0.93, 0.12, 0.02, 0.78])  # [left, bottom, width, height]

    # One colour bar normalised by the global min and max probabilities
    fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(p_min, p_max), cmap=colour), cax=cbar_ax, label=label)
    fig.suptitle(title, fontsize=24)

    return fig


def main(): 
    number_of_bins = 10     # For discretisation of indicator values by percentile
    holding_period = 20     # Period limit for outcome to resolve - handled as unresolved if A or B thresholds do not hit

    indicator_id = 1
    percentile_bin = 8

    # Fetch raw data and process outcomes dataframe with probabilites for each threshold pair for each bin
    df_outcomes = fetch_data(number_of_bins, holding_period)
    df_outcomes['probability'] = df_outcomes['a_hit_before_b'] / df_outcomes['bin_candle_count']
    df_outcomes = df_outcomes.loc[df_outcomes['indicator_id'] == indicator_id]      # Filter to selected indicator ID

    # Probability heatmap for single bin
    bin_probability_contingency = get_bin_probability_contingency(df_outcomes, percentile_bin)
    title = f"Probability of Threshold A before Threshold B\nIndicator ID {indicator_id}, Percentile Bin {percentile_bin}"
    plot_heatmap(bin_probability_contingency, colour='viridis', title=title)

    # All probability heatmaps on one heatmap
    multi_contingency = df_outcomes.pivot_table(values='probability', index='threshold_a', columns=['percentile_bin', 'threshold_b'])   # Multi column index
    title = f"Probability of Threshold A Before Threshold B\nIndicator ID {indicator_id}, All Percentile Bins Multi-Index"
    plot_multi_heatmap(multi_contingency, colour='viridis', title=title)

    # Probability heatmap for all bins in one figure
    all_bin_probability_contingencies = get_all_bin_contingencies(df_outcomes, get_bin_probability_contingency)
    title = f"Probability of Threshold A Before Threshold B\nIndicator ID {indicator_id}, All Percentile Bins"
    plot_all_heatmaps(all_bin_probability_contingencies, label="probability", colour="viridis", title=title)

    # EV heatmap for single bin
    bin_ev_contingency = get_bin_ev_contingency(df_outcomes, percentile_bin)
    title = f"Expected Value for Take-Profit/Stop-Loss Setup\nFor Indicator ID {indicator_id} in Percentile Bin {percentile_bin}"
    plot_heatmap(bin_ev_contingency, colour='RdBu', title=title, center=0)
  
    # EV heatmap for all bins in one figure
    all_bin_ev_contingencies = get_all_bin_contingencies(df_outcomes, get_bin_ev_contingency)
    title = f"Expected Value for Take-Profit/Stop-Loss Setup\nIndicator ID {indicator_id}, All Percentile Bins"
    plot_all_heatmaps(all_bin_ev_contingencies, label="ev", colour="RdBu", title=title)

    plt.show()


if __name__ == "__main__":
    main()