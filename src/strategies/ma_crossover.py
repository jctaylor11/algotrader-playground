import pandas as pd
import matplotlib.pyplot as plt

def ma_crossover_strategy(data):
    # So it doesn't interfere with original data passed in
    data = data.copy()          

    # Intialising all positions to 0
    data['position'] = 0        

    # Setting ma strategy parameters
    MA_S = 50
    MA_L = 100

    # Calculating the MA prices
    data['ma_s'] = data['close'].rolling(window=MA_S).mean()
    data['ma_l'] = data['close'].rolling(window=MA_L).mean()

    # Strategy conditions
    data['condition'] = data['ma_s'] > data['ma_l']

    # Strategy implementation
    data.loc[data['condition'], 'position'] = 1

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

    return data['position']

