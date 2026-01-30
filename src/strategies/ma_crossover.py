import pandas as pd
import matplotlib.pyplot as plt

from src.visualisation.plot_trades import plot_trades

def ma_crossover_strategy(data, params):
    # So it doesn't interfere with original data passed in
    data = data.copy()          

    # Intialising all positions to 0
    data['position'] = 0        

    # Setting ma strategy parameters
    MA_S = params[0]
    MA_L = params[1]

    # Calculating the MA prices
    data['ma_s'] = data['close'].rolling(window=MA_S).mean()
    data['ma_l'] = data['close'].rolling(window=MA_L).mean()

    # Strategy conditions
    data['condition'] = data['ma_s'] > data['ma_l']

    # Strategy implementation
    data.loc[data['condition'], 'position'] = 1

    # fig, ax = plot_trades(data, ['ma_s', 'ma_l'])
    # ax.set_title('Moving Average Strategy Visualisation')
    # plt.show()

    return data['position']


