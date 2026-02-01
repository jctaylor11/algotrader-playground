from itertools import product
import numpy as np
import pandas as pd

from src.strategies.ma_crossover import ma_crossover_strategy

def grid_search_strategy(df, strategy, params_dict: dict[str, range | list]) -> pd.DataFrame:    
    dict_keys = list(params_dict.keys())
    dict_values = params_dict.values()

    dict_values_combinations =list(product(*dict_values))

    results_list = []
    for combination in dict_values_combinations:
        # Builds a list which represents one instance of the strategy with the given combination of parameters
        strategy_result = list(combination) + [_strategy_iterator(df, strategy, combination)]

        # Appends that instance to the list of strategy performance results
        results_list.append(strategy_result)
        
    # Turning to dataframe and adding the columns
    columns = dict_keys + ['performance']
    results = pd.DataFrame(results_list, columns=columns)
    results['performance'] = results['performance'].round(2)     # Cleaner rounded to 2dp

    return results


def grid_search_optimal_params(results) -> dict: 
    # Finding the optimal strategy from all the simulations
    index_of_optimal = results['performance'].idxmax()
    optimal_params = results.iloc[index_of_optimal]

    # Packaging it up as a dict to return
    optimal_params_dict = optimal_params.to_dict()

    print(results)
    print("\n-- Optimal Strategy Params --")
    final_keys = optimal_params_dict.keys()
    for key in final_keys:
        print(f"{key.upper()}: {optimal_params_dict[key]}")
    print("")

    return optimal_params_dict


def _strategy_iterator(df, strategy, params_list):
    """optimise_strategy_params helper function, to run one instance of the strategy with the given combination of parameters"""
    df = df.copy()
    df['position'] = strategy(df, params_list)

    # Calculate the strategy returns with those parameters
    df['log_return'] = np.log(df['close'].div(df['close'].shift(1)))
    df['strategy_log_return'] = df['position'].shift(1)* df['log_return']
    df['cum_strategy'] = np.exp(df['strategy_log_return'].cumsum())

    # Return the chosen performance indicator - currently the Multiple to start basic
    return float(df['cum_strategy'].iloc[-1])


# Just for testing module
if __name__ == "__main__":
    params = {'A': range(0, 10, 1), 'B': range(10, 20, 1)}
    df = pd.read_csv("data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv", parse_dates=['date'], index_col='date')
    df = df[['close', 'volume']].loc['2021'].copy()
    results = grid_search_strategy(df, ma_crossover_strategy, params_dict=params)
    optimal_params = grid_search_optimal_params(results)
    print(optimal_params)