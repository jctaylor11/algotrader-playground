import pandas as pd
import matplotlib.pyplot as plt

from src.visualisation.plot_trades import plot_trades, overlay_trades


def ma_crossover_strategy(close, params):
    # So it doesn't interfere with original data passed in
    close = close.copy()               

    # Setting ma strategy parameters
    MA_S = params[0]
    MA_L = params[1]

    # Calculating the MA prices
    ma_s = close.rolling(window=MA_S).mean()
    ma_l = close.rolling(window=MA_L).mean()

    # Setting the series names, since by default it inherits from original series ('close')
    ma_s.name = 'ma_s'
    ma_l.name = 'ma_l'

    # Strategy conditions
    condition = pd.Series(ma_s > ma_l)

    # Strategy implementation
    position = pd.Series(0, index=close.index)   # Initialise all positions to 0 with same index as close
    position[condition] = 1 

    fig, ax = plot_trades(close, [ma_s, ma_l])
    ax.set_title('Moving Average Strategy Visualisation')
    ax = overlay_trades(position, ax)       

    plt.show()

    return position


# def ma_crossover_strategy(data, params):
#     # So it doesn't interfere with original data passed in
#     data = data.copy()          

#     # Intialising all positions to 0
#     data['position'] = 0        

#     # Setting ma strategy parameters
#     MA_S = params[0]
#     MA_L = params[1]

#     # Calculating the MA prices
#     data['ma_s'] = data['close'].rolling(window=MA_S).mean()
#     data['ma_l'] = data['close'].rolling(window=MA_L).mean()

#     # Strategy conditions
#     data['condition'] = data['ma_s'] > data['ma_l']

#     # Strategy implementation
#     data.loc[data['condition'], 'position'] = 1

#     fig, ax = plot_trades(data, ['ma_s', 'ma_l'])
#     ax.set_title('Moving Average Strategy Visualisation')
#     plt.show()

#     return data['position']


