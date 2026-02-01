import pandas as pd
import numpy as np


def get_performance_metrics(data):
    data = data.copy()
    data_interval = data.index.diff().median()          # Takes the median than any absolute for reliability
    annual_periods = pd.Timedelta(days=365.25) / data_interval  # Infers number of periods over the year from the data, for mu and stdev

    ann_mean = _calculate_ann_mean(data, annual_periods)
    ann_std = _calculate_ann_std(data, annual_periods)

    sharpe = _calculate_sharpe_ratio(ann_mean, ann_std)

    performance = pd.concat([ann_mean, ann_std, sharpe], axis=1)

    return performance


def _calculate_ann_mean(data, annual_periods):
    """Takes log data, returns a series containing results for each log column"""
    ann_mean_log = data[['log_return', 'strategy_log_return', 'strategy_log_net']].mean() * annual_periods     # Return is log return, and annual periods is inferred from index
    ann_mean = np.exp(ann_mean_log) - 1

    ## Alternate Method: ann_mean = ((1 + cum_return) ^ (annual_periods / duration)) - 1
    # cum_log_return = data[['log_return', 'strategy_log_return', 'strategy_log_net']].sum()
    # cum_return = np.exp(cum_log_return) - 1 
    # ann_mean = (1 + cum_return) ** (annual_periods / len(data)) - 1
    # ann_mean.name = 'Annualised Mean'

    ann_mean.name = 'Annualised Mean'
    ann_mean.index = ['Buy & Hold', 'Strategy', 'Strategy Net']

    return ann_mean


def _calculate_ann_std(data, annual_periods):
    """Takes log data, returns a series containing results for each log column"""
    ann_std = data[['log_return', 'strategy_log_return', 'strategy_log_net']].std() * np.sqrt(annual_periods)
    ann_std.index = ['Buy & Hold', 'Strategy', 'Strategy Net']
    ann_std.name = 'Annualised StDev'
    return ann_std


def _calculate_sharpe_ratio(annualised_mean, annualised_std):
    sharpe = annualised_mean / annualised_std
    sharpe.name = 'Sharpe Ratio'
    return sharpe