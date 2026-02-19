import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate

from src.reporting.performance_metrics import get_performance_metrics
from src.visualisation.results_plots import overlay_trades
from src.backtest.fees import apply_trading_commissions
from src.analysis.optimisation import grid_search_strategy, grid_search_optimal_params


class Backtester:
    def __init__(self, dataframe, start, end, strategy_function, strategy_params:dict=None):
        self.input_df = dataframe
        self.start = start
        self.end = end
        self.strategy_function = strategy_function
        self.strategy_params = strategy_params

        self.raw_data = self.get_data()
        self.results = None
        self.commission = 0.1 / 100     # Hard-coded for now

    @classmethod
    def with_csv(cls, filepath, start, end, strategy_function, strategy_params:dict=None):
        dataframe = pd.read_csv(filepath, parse_dates=['date'], index_col='date')
        return cls(dataframe, start, end, strategy_function, strategy_params)

    def get_data(self):
        data = self.input_df.copy()
        
        # Validate correct format
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data["date"])
            data = data.set_index('date')
        elif data.index.name == 'date':
            data.index = pd.to_datetime(data.index)
        else:
            raise ValueError("DateFrame must have a date column or 'date' as index name")
            
        data = data.loc[self.start:self.end]
        return data

    def optimise_strategy_params(self, optimisation_params, verbose=True): 
        parameter_grid = grid_search_strategy(self.raw_data, self.strategy_function, optimisation_params)
        optimal_strategy_params = grid_search_optimal_params(parameter_grid)

        if verbose:
            print("\nOptimal Strategy Params:")
            final_keys = optimal_strategy_params.keys()
            for key in final_keys:
                print(f"    {key.upper()}: {optimal_strategy_params[key]}")
            print("")

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
                performance_metrics[col] = performance_metrics[col].map("{:.0%}".format)
            else:
                performance_metrics[col] = performance_metrics[col].map("{:.2f}".format)

        print(tabulate(performance_metrics, headers='keys', tablefmt='pretty'))

        return performance_metrics
    
    def get_results(self):
        return self.results
    
    def get_positions(self):
        return self.results['position']

    def plot_matplotlib(self):
        if self.results is None:
            print("No results yet - run 'run_strategy_backtest()' first")
            return
    
        fig, ax = plt.subplots(figsize=(12,8))
        self.results[['cum_return', 'cum_strategy', 'cum_strategy_net']].plot(ax=ax)
        ax.legend(['Buy and Hold', 'Your Strategy', 'Your strategy (with fees)'])
        ax.set_title('Strategy Backtest Performance')
        
        return fig, ax
    