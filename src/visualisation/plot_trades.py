import pandas as pd
import matplotlib.pyplot as plt


def plot_trades(close, indicators=None):
    """Plot the price data including indicators in the original dataset"""
    if indicators is None:
        indicators = []

    # Create the figure and axis to plot onto, and plot the close data
    fig, ax = plt.subplots(figsize=(12,8))   
    close.plot(ax=ax)

    # Overlay the specified indicators on the same ax 
    for indicator in indicators: 
        try:
            indicator.plot(ax=ax, label=indicator.name)
        except NameError as e:
            print(f"Error: {e}")
    
    ax.legend()

    return fig, ax


def overlay_trades(position, ax):
    """Takes data and an ax and overlays trades. In this way you can apply trade data to any final chart"""
    position = position.copy()

    # Calculate trade events
    trade = position.diff()

    # Use for drawing vertical lines
    ymin, ymax = ax.get_ylim()        

    # For all buys
    buy_times = trade[trade == 1].index
    ax.vlines(buy_times, ymin, ymax, color='green', linestyle='dotted')

    # For all sells
    sell_times = trade[trade == -1].index
    ax.vlines(sell_times, ymin, ymax, color='red', linestyle='dashed')

    return ax