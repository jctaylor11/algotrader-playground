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

    # Performance metrics
    data_interval = data.index.diff().median()          # Takes the median than any absolute for reliability
    annual_periods = pd.Timedelta(days=365.25) / data_interval  # Infers number of periods over the year from the data, for mu and stdev

    ann_mean_log = data[['Return', 'Strategy']].mean() * annual_periods     # Return is log return, and annual periods is inferred from index
    ann_mean = np.exp(ann_mean_log) - 1
    ann_mean.name = 'Annualised Mean'

    ann_std = data[['Return', 'Strategy']].std() * np.sqrt(annual_periods)
    ann_std.name = 'Annualised StDev'

    sharpe = ann_mean / ann_std
    sharpe.name = 'Sharpe Ratio'

    performance = pd.concat([ann_mean, ann_std, sharpe], axis=1)
    print(performance)

    # Apply trading commissions
    commission = 0.1 / 100 
    log_commission_multiplier = np.log(1 - commission)        # To multiply (add in log space) strategy returns with to get net return per trade after fees 
    data['Trade'] = data['Position'].diff().fillna(0).abs()         # 1 in every entry where a trade took place
    data['Strategy_net'] = data['Strategy'] + data['Trade'] * log_commission_multiplier
    data['C_strategy_net'] = data['Strategy_net'].cumsum().apply(np.exp)

    # Plot results
    data[['C_return', 'C_strategy', 'C_strategy_net']].plot(figsize=(12,8))
    plt.legend(['Buy and Hold', 'Your Strategy', 'Your strategy (with fees)'])
    plt.show()


backtester()

