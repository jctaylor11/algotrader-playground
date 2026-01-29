import pandas as pd
import matplotlib.pyplot as plt

def plot_trades(data):
    # Strategy trades visualisation - Draw a vertical line each time a trade occurs
    data['trade'] = data['position'].diff()

    # Create the figure and axis to plot onto
    fig, myax = plt.subplots(figsize=(12,8))   
    data[['close', 'ma_s', 'ma_l']].plot(ax=myax)

    # Use for drawing vertical lines
    ymin, ymax = myax.get_ylim()        

    # For all buys
    buy_times = data.loc[data['trade'] == 1].index
    myax.vlines(buy_times, ymin, ymax, color='green', linestyle='dotted')

    # For all sells
    sell_times = data.loc[data['trade'] == -1].index
    myax.vlines(sell_times, ymin, ymax, color='red', linestyle='dashed')

    plt.show()
    