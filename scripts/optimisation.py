import pandas as pd

from src.strategies.ma_crossover import ma_crossover_strategy
from src.analysis.optimisation import grid_search_strategy, grid_search_optimal_params

# Load data
df = pd.read_csv("data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv", parse_dates=['date'], index_col='date')
df = df[['close', 'volume']].loc['2021'].copy()

# Strategy configuration
strategy = ma_crossover_strategy
strategy_params = {
    "ma_s": range(50, 100, 1),
    "ma_l": range(150, 200, 1)
}

# Optimisation pipeline
strategy_simulations = grid_search_strategy(df, strategy, strategy_params)
optimal_params = grid_search_optimal_params(strategy_simulations)

print(optimal_params)