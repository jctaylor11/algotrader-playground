from itertools import product
import numpy as np
import pandas as pd

from src.strategies.ma_crossover import ma_crossover_strategy

def optimise_strategy_params(df, strategy, params_dict: dict[str, range | list]) -> dict:    
    dict_keys = list(params_dict.keys())
    dict_values = params_dict.values()

    dict_values_combinations =list(product(*dict_values))

    performance_results = []
    for combination in dict_values_combinations:
        # Builds a list which represents one instance of the strategy with the given combination of parameters
        strategy_result = list(combination) + [_strategy_iterator(df, strategy, combination)]

        # Appends that instance to the list of strategy performance results
        performance_results.append(strategy_result)
        
    # Turning to dataframe and adding the columns
    results = pd.DataFrame(performance_results)
    columns = dict_keys + ['performance']
    results.columns = columns

    # Finding the optimal strategy from all the simulations
    index_of_optimal = results['performance'].idxmax()
    optimal_strategy = results.iloc[index_of_optimal]

    # Packaging it up as a dict to return
    optimal_strategy_dict = optimal_strategy.to_dict()

    print(results)
    print("\n-- Optimal Strategy Params --")
    final_keys = optimal_strategy_dict.keys()
    for key in final_keys:
        print(f"{key.upper()}: {optimal_strategy_dict[key]}")
    print("")

    return optimal_strategy_dict


def _strategy_iterator(df, strategy, params_list):
    """optimise_strategy_params helper function, to run one instance of the strategy with the given combination of parameters"""
    df = df.copy()
    df['position'] = strategy(df, params_list)

    # Calculate the strategy returns with those parameters
    df['return'] = np.log(df['close'].div(df['close'].shift(1)))
    df['strategy_returns'] = df['position'].shift(1)* df['return']
    df['cum_strategy'] = np.exp(df['strategy_returns'].cumsum())

    # Return the chosen performance indicator - currently the Multiple to start basic
    return float(df['cum_strategy'].iloc[-1])


# Just for testing module
if __name__ == "__main__":
    params = {'A': range(0, 10, 1), 'B': range(10, 20, 1)}
    df = pd.read_csv("data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv", parse_dates=['date'], index_col='date')
    df = df[['close', 'volume']].loc['2021'].copy()
    optimise_strategy_params(df, ma_crossover_strategy, params_dict=params)