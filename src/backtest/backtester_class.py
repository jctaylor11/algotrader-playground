import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.strategies.ma_crossover import ma_crossover_strategy
from src.reporting.performance_metrics import get_performance_metrics
from src.visualisation.plot_trades import overlay_trades


class Backtester():
    def __init__(self, filepath, start, end):
        self.filepath = filepath
        self.start = start
        self.end = end
        self.get_data()
        self.results = None
    
    def get_data(self):
        data = pd.read_csv(self.filepath, parse_dates=['date'], index_col='date')
        data = data[['close', 'volume']]
        data = data.loc[self.start:self.end].copy()
        self.raw_data = data

    def run_strategy_backtest(self):
        data = self.raw_data.copy() 

        # Buy and hold strategy as benchmark to compare strategy - TODO: Consider extracting this as a 'calculate_bh_benchmark' function
        data['simple_return'] = data['close'].div(data['close'].shift(1))
        data['log_return'] = np.log(data['simple_return'])
        data['cum_return'] = np.exp(data['log_return'].cumsum())    

        # Apply Strategy (no trading commissions)
        data['position'] = ma_crossover_strategy(data['close'], [50, 150])             # TODO: Strategy can be passed in as argument for reusability
        data['strategy_log_return'] = data['position'].shift(1) * data['log_return']
        data['cum_strategy'] = np.exp(data['strategy_log_return'].cumsum())

        # Apply trading commissions
        commission = 0.1 / 100 
        log_commission_multiplier = np.log(1 - commission)        # Add to strategy_log_return to get net return per trade after fees
        data['trade'] = data['position'].diff().fillna(0).abs()         # 1 in every entry where a trade took place
        data['strategy_log_net'] = data['strategy_log_return'] + (data['trade'] * log_commission_multiplier)
        data['cum_strategy_net'] = np.exp(data['strategy_log_net'].cumsum())

        # Save the results as an attribute
        self.results = data

    def print_performance(self):
        performance_metrics = get_performance_metrics(self.results)
        print(performance_metrics)

    def plot_results(self):
        fig, ax = plt.subplots(figsize=(12,8))
        self.results[['cum_return', 'cum_strategy', 'cum_strategy_net']].plot(ax=ax)
        ax = overlay_trades(self.results['position'], ax)
        ax.legend(['Buy and Hold', 'Your Strategy', 'Your strategy (with fees)'])
        ax.set_title('Strategy Backtest Performance')
        plt.show()

    
# For testing
if __name__ == '__main__':
    # Configure backtester
    filepath = 'data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv'
    start = '2021-01-01'
    end = '2022-02-02'

    # Instantiate backtester from Backtester class
    bot = Backtester(filepath=filepath, start=start, end=end)
    bot.run_strategy_backtest()
    bot.print_performance()
    bot.plot_results()
