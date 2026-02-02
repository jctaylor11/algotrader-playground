import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.strategies.ma_crossover import ma_crossover_strategy
from src.visualisation.plot_trades import plot_trades, overlay_trades
from src.reporting.performance_metrics import get_performance_metrics


def backtester():
    # Getting data
    data = pd.read_csv('data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv', parse_dates=['date'], index_col='date')
    data = data[['close', 'volume']]
    data = data.loc['2025-01':'2025-02'].copy()

    # Buy and hold strategy as benchmark to compare strategy
    data['simple_return'] = data['close'].div(data['close'].shift(1))
    data['log_return'] = np.log(data['simple_return'])
    data['cum_return'] = np.exp(data['log_return'].cumsum())    

    # Strategy
    data['position'] = ma_crossover_strategy(data['close'], [50, 150])

    # Calculate return from strategy positions
    data['strategy_log_return'] = data['position'].shift(1) * data['log_return']
    data['cum_strategy'] = np.exp(data['strategy_log_return'].cumsum())

    # Apply trading commissions
    commission = 0.1 / 100 
    log_commission_multiplier = np.log(1 - commission)        # Add to strategy_log_return to get net return per trade after fees
    data['trade'] = data['position'].diff().fillna(0).abs()         # 1 in every entry where a trade took place
    data['strategy_log_net'] = data['strategy_log_return'] + (data['trade'] * log_commission_multiplier)
    data['cum_strategy_net'] = np.exp(data['strategy_log_net'].cumsum())

    # Performance metrics
    performance_metrics = get_performance_metrics(data)
    print(performance_metrics)

    # Plot results
    fig, ax = plt.subplots(figsize=(12,8))
    data[['cum_return', 'cum_strategy', 'cum_strategy_net']].plot(ax=ax)
    ax = overlay_trades(data['position'], ax)
    ax.legend(['Buy and Hold', 'Your Strategy', 'Your strategy (with fees)'])
    ax.set_title('Strategy Backtest Performance')
    plt.show()


backtester()

