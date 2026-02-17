import pandas as pd
import matplotlib.pyplot as plt


def ma_crossover_strategy(data, params:dict):
    # So it doesn't interfere with original data passed in  
    close = data['close'].copy()           

    # Setting ma strategy parameters
    MA_S = params['ma_s']
    MA_L = params['ma_l']

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

    return position
