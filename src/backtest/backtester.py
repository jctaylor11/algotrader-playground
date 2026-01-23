import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def backtester():
    # Getting data
    data = pd.read_csv('data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv', parse_dates=['Date'], index_col='Date')
    data = data[['Close', 'Volume']]
    data = data.loc['2025'].copy()

    # Buy and hold strategy as benchmark to compare strategy
    data['Return'] = data['Close'].div(data['Close'].shift(1))
    data['Return'] = np.log(data['Return'])
    data['C_return'] = data['Return'].cumsum().apply(np.exp)        # C for cumulative results

    # Strategy
    data['Position'] = 1
    sell_condition = data['Close'] % 10 == 0            # Random strategy for now - sells whenever price is a multiple of 10 
    data.loc[sell_condition, 'Position'] = 0
    data['Strategy'] = data['Position'].shift(1) * data['Return']
    data['C_strategy'] = data['Strategy'].cumsum().apply(np.exp)

    # Show results
    data[['C_return', 'C_strategy']].plot(figsize=(12,8))
    plt.legend(['Buy and Hold', 'Your Strategy'])
    plt.show()
 




backtester()

