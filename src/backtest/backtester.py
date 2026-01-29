import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.strategies.ma_crossover import ma_crossover_strategy
from src.visualisation.plot_trades import plot_trades

def backtester():
    # Getting data
    data = pd.read_csv('data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv', parse_dates=['date'], index_col='date')
    data = data[['close', 'volume']]
    data = data.loc['2021-01':'2021-02'].copy()

    # Buy and hold strategy as benchmark to compare strategy
    data['return'] = data['close'].div(data['close'].shift(1))
    data['return'] = np.log(data['return'])
    data['c_return'] = np.exp(data['return'].cumsum())     # C for cumulative results

    # Strategy
    data['position'] = ma_crossover_strategy(data)

    data['strategy'] = data['position'].shift(1) * data['return']
    data['c_strategy'] = np.exp(data['strategy'].cumsum())

    # Performance metrics
    data_interval = data.index.diff().median()          # Takes the median than any absolute for reliability
    annual_periods = pd.Timedelta(days=365.25) / data_interval  # Infers number of periods over the year from the data, for mu and stdev

    ann_mean_log = data[['return', 'strategy']].mean() * annual_periods     # Return is log return, and annual periods is inferred from index
    ann_mean = np.exp(ann_mean_log) - 1
    ann_mean.name = 'Annualised Mean'

    ann_std = data[['return', 'strategy']].std() * np.sqrt(annual_periods)
    ann_std.name = 'Annualised StDev'

    sharpe = ann_mean / ann_std
    sharpe.name = 'Sharpe Ratio'

    performance = pd.concat([ann_mean, ann_std, sharpe], axis=1)
    print(performance)

    # Apply trading commissions
    commission = 0.1 / 100 
    log_commission_multiplier = np.log(1 - commission)        # To multiply (add in log space) strategy returns with to get net return per trade after fees 
    data['trade'] = data['position'].diff().fillna(0).abs()         # 1 in every entry where a trade took place
    data['strategy_net'] = data['strategy'] + data['trade'] * log_commission_multiplier
    data['c_strategy_net'] = np.exp(data['strategy_net'].cumsum())

    # Plot results
    data[['c_return', 'c_strategy', 'c_strategy_net']].plot(figsize=(12,8))
    plt.legend(['Buy and Hold', 'Your Strategy', 'Your strategy (with fees)'])
    plt.show()


backtester()

