import pandas as pd
import matplotlib.pyplot as plt

def plot_trades(data, indicators=None):
    """I could enhance this to calculate the specified indicator and add it, if it doesn't already exist (though may be tricky with consistent naming/identification)"""
    if indicators is None:
        indicators = []

    data = data.copy()
    data['trade'] = data['position'].diff()

    # Create the figure and axis to plot onto, and plot the close data
    fig, myax = plt.subplots(figsize=(12,8))   
    data['close'].plot(ax=myax)

    # Overlay on the same ax the specified indicators
    for indicator in indicators:                # Add error checking to see that column actually exists
        try:
            data[indicator].plot(ax=myax)
        except KeyError:
            print(f"'{indicator}' is not a column in dataframe - excluded from plot")

    # Use for drawing vertical lines
    ymin, ymax = myax.get_ylim()        

    # For all buys
    buy_times = data.loc[data['trade'] == 1].index
    myax.vlines(buy_times, ymin, ymax, color='green', linestyle='dotted')

    # For all sells
    sell_times = data.loc[data['trade'] == -1].index
    myax.vlines(sell_times, ymin, ymax, color='red', linestyle='dashed')

    plt.show()
    