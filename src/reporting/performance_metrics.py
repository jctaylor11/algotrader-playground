import pandas as pd
import numpy as np


def get_performance_metrics(data):
    data = data.copy()

    cagr = _calculate_cagr(data)
    ann_std = _calculate_ann_std(data)
    sharpe = _calculate_sharpe_ratio(cagr, ann_std)

    performance_results = pd.concat([cagr, ann_std, sharpe], axis=1)

    return performance_results


def _calculate_cagr(data):
    """
    Takes log data, returns a series cagr for each log column
    
    Assumes the first row is the starting point by setting the first row to zero (likely from NAs).
    """
    log_return_cols = ['log_return', 'strategy_log_return', 'strategy_log_net']
    data.loc[data.index[0], log_return_cols] = 0    # Setting the first row to 0 to remove na and ensure starting point

    start_value = np.exp(data[log_return_cols].cumsum().iloc[0])  
    end_value = np.exp(data[log_return_cols].cumsum().iloc[-1])  
    multiple = end_value / start_value

    # cagr = (ending value / starting value) ** (1 / number of years) - 1
    start_date = data.index[0]
    end_date = data.index[-1]
    num_years = (end_date - start_date).days / 365.2

    print(f"num_years: {num_years}")

    cagr = (multiple ** (1 / num_years) - 1)
    cagr.name = 'CAGR'
    cagr.index = ['Buy & Hold', 'Strategy', 'Strategy Net']

    return cagr


def _calculate_ann_std(data):
    """Takes log data, returns a series containing results for each log column"""
    # Using the data interval to calculate number of periods in the year, to annualise stdev
    data_interval = data.index.diff().median()          # Takes the median than any absolute for reliability
    trading_periods_per_year = pd.Timedelta(days=365.25) / data_interval

    ann_std = data[['log_return', 'strategy_log_return', 'strategy_log_net']].std() * np.sqrt(trading_periods_per_year)
    ann_std.index = ['Buy & Hold', 'Strategy', 'Strategy Net']
    ann_std.name = 'Annualised log StDev'
    return ann_std


def _calculate_sharpe_ratio(cagr, annualised_std):
    sharpe = cagr / annualised_std
    sharpe.name = 'Sharpe Ratio'
    return sharpe