import numpy as np
import pandas as pd
from itertools import product

from src.strategies.ma_crossover import ma_crossover_strategy


def main():
    """Optimisation script to find optimal moving average combination for ma_crossover strategy"""
    # Load data
    df = pd.read_csv("data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv", parse_dates=['date'], index_col='date')
    df = df[['close', 'volume']].loc['2021'].copy()

    # Generate all possible combinations with itertools
    ma_s_range = range(50, 100, 1)
    ma_l_range = range(150, 200, 1)
    combinations = list(product(ma_s_range, ma_l_range))

    # Populate empty array with performance for all different combinations
    performance_results = []
    for combination in combinations:
        performance_results.append([combination[0], combination[1], strategy_backtest(df, combination)])        # TODO: Seems inefficient, perhaps a vectorised way
    
    results = pd.DataFrame(performance_results)
    results.columns = ['MA_S', 'MA_L', 'Performance']
    
    optimal_index = results['Performance'].idxmax()
    optimal_params = results.iloc[optimal_index]

    print(f"Optimal performance of {optimal_params['Performance']:.2f} with {optimal_params['MA_S']} and {optimal_params['MA_L']}")        # Hardcoded for now


def strategy_backtest(df, params):
    df = df.copy()
    df['position'] = ma_crossover_strategy(df, params)

    # See performance metrics - take multiple
    df['return'] = np.log(df['close'].div(df['close'].shift(1)))
    df['strategy_returns'] = df['position'].shift(1)* df['return']
    df['cum_strategy'] = np.exp(df['strategy_returns'].cumsum())

    # Using the mutliple as performance indicator 
    return float(df['cum_strategy'].iloc[-1])


main()