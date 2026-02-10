import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.reporting.performance_metrics import get_performance_metrics
from src.visualisation.plot_trades import overlay_trades
from src.backtest.fees import apply_trading_commissions
from src.analysis.optimisation import grid_search_strategy, grid_search_optimal_params


class Backtester():
    def __init__(self, filepath, start, end, strategy_function, strategy_params: dict):
        self.filepath = filepath
        self.start = start
        self.end = end
        self.strategy_function = strategy_function
        self.strategy_params = strategy_params

        self.raw_data = self.get_data()
        self.results = None
        self.commission = 0.1 / 100     # Hard-coded for now

    def get_data(self):
        data = pd.read_csv(self.filepath, parse_dates=['date'], index_col='date')
        data = data.loc[self.start:self.end].copy()
        return data

    def optimise_strategy_params(self, optimisation_params): 
        parameter_grid = grid_search_strategy(self.raw_data, self.strategy_function, optimisation_params)
        optimal_strategy_params = grid_search_optimal_params(parameter_grid)
        return optimal_strategy_params

    def run_strategy_backtest(self):
        data = self.raw_data.copy() 

        # Calculate returns for Buy and Hold benchmark (cum_return)
        data['simple_return'] = data['close'].div(data['close'].shift(1))
        data['log_return'] = np.log(data['simple_return'])
        data['cum_return'] = np.exp(data['log_return'].cumsum())   
        
        # Apply Strategy (no trading commissions)
        data['position'] = self.strategy_function(self.raw_data, self.strategy_params) 
        data['strategy_log_return'] = data['position'].shift(1) * data['log_return']
        data['cum_strategy'] = np.exp(data['strategy_log_return'].cumsum())

        # Apply trading commissions
        data = apply_trading_commissions(data, self.commission) 

        # Save the results as an attribute
        self.results = data

    def print_performance(self):
        if self.results is None:
            print("No results yet - run 'run_strategy_backtest()' first")
            return
        
        performance_metrics = get_performance_metrics(self.results)

        for col in performance_metrics.columns:
            if col == 'CAGR':
                performance_metrics[col] = performance_metrics[col].map("{:.2%}".format)
            else:
                performance_metrics[col] = performance_metrics[col].map("{:.2f}".format)

        print(performance_metrics)

    def plot_results(self):
        if self.results is None:
            print("No results yet - run 'run_strategy_backtest()' first")
            return
    
        fig, ax = plt.subplots(figsize=(12,8))
        self.results[['cum_return', 'cum_strategy', 'cum_strategy_net']].plot(ax=ax)
        ax = overlay_trades(self.results['position'], ax)
        ax.legend(['Buy and Hold', 'Your Strategy', 'Your strategy (with fees)'])
        ax.set_title('Strategy Backtest Performance')
        plt.show()