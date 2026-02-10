import pandas as pd
import numpy as np


def get_performance_metrics(data):
    data = data.copy()

    cagr = _calculate_cagr(data)
    ann_std = _calculate_ann_simple_std(data)
    sharpe = _calculate_sharpe_ratio(data)

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

    cagr = (multiple ** (1 / num_years) - 1)
    cagr.name = 'CAGR'
    cagr.index = ['Buy & Hold', 'Strategy', 'Strategy Net']

    return cagr


def _calculate_ann_simple_std(data):
    """Takes log data, returns a series containing simple stdev"""
    # Using the data interval to calculate number of periods in the year, to annualise stdev
    data_interval = data.index.diff().median()          # Takes the median than any absolute for reliability
    trading_periods_per_year = pd.Timedelta(days=365.25) / data_interval


    simple_returns = np.exp(data[['log_return', 'strategy_log_return', 'strategy_log_net']]) - 1
    ann_std = simple_returns.std() * np.sqrt(trading_periods_per_year)      # Simple standard deviation annualised

    ann_std.index = ['Buy & Hold', 'Strategy', 'Strategy Net']
    ann_std.name = 'Annualised Simple StDev'
    return ann_std


def _calculate_ann_log_std(data):
    """
    Takes log data, returns a series containing log stdev.

    log std is mathematically consistent with my usage of log returns, though simple std is more common for reporting. 
    I have I therefore included functions for both simple and log std, for more explicit clarity, and options for mathematical consistency and reporting convention.
    """
    data_interval = data.index.diff().median()         
    trading_periods_per_year = pd.Timedelta(days=365.25) / data_interval

    # Standard deviation of log returns
    ann_log_std = data[['log_return', 'strategy_log_return', 'strategy_log_net']].std() * np.sqrt(trading_periods_per_year)

    ann_log_std.index = ['Buy & Hold', 'Strategy', 'Strategy Net']
    ann_log_std.name = 'Annualised Log StDev'
    return ann_log_std


def _calculate_sharpe_ratio(data, periodic_risk_free_rate=0.0, rf_nperiods=None, annualise=True):
    """
    Calculates the Sharpe Ratio for each strategy in the data.

    Calculated using the return of the portfolio (minus risk free rate) divided by the (simple) annualised standard deviation.
    rf_nperiods is the number of periods the risk free rate corresponds to. If None, it assumes the risk free rate is for the same frequency as the data.
    Periods is in the same interval as the data. For example, for daily data and an annual risk free rate, rf_nperiods=365.25 (for 24-hour markets)

    Approach regarding usage of simple returns and simple standard deviation is consistent with Quantstats approach.
    Source: https://github.com/ranaroussi/quantstats/blob/main/quantstats/stats.py#l272 

    """
    # Standard convention is to use simple returns for Sharpe ratio calculation - which feels wrong, but is standard practice
    simple_returns = np.exp(data[['log_return', 'strategy_log_return', 'strategy_log_net']]) - 1

    if rf_nperiods is not None:
        rf_rate_periodic = (1 + periodic_risk_free_rate) ** (1 / rf_nperiods) - 1
    else:
        rf_rate_periodic = periodic_risk_free_rate
    
    excess_simple_returns = simple_returns - rf_rate_periodic
    mean_return = excess_simple_returns.mean()

    sharpe = mean_return / excess_simple_returns.std(ddof=1)  # ddof=1 since data is sample rather than population

    if annualise == True: 
        data_frequency = data.index.diff().median()
        num_periods_per_year = pd.Timedelta(days=365.25) / data_frequency

        # Annualised - returns scale linearly but stdev scales by sqrt, hence annualisation multipler: num / sqrt(num) = sqrt(num)
        sharpe = sharpe * np.sqrt(num_periods_per_year)

    sharpe.name = 'Sharpe Ratio'
    sharpe.index = ['Buy & Hold', 'Strategy', 'Strategy Net']

    return sharpe

