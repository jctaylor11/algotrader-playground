from src.reporting.performance_metrics import _calculate_ann_mean, _calculate_ann_std

import pandas as pd
import numpy as np

# Starting with known simple daily returns to verify annualisation calculations
simple_daily_return = 0.0001
simple_strategy_daily_return = 0.00015

# Generate known annual data
annual_periods = 365
dates = pd.date_range(start='2025-01-01', periods=annual_periods, freq='D')
synthetic_data = pd.DataFrame({
    'log_return': [np.log(1 + simple_daily_return)] * len(dates),
    'strategy_log_return': [np.log(1 + simple_strategy_daily_return)] * len(dates),
    'strategy_log_net': [np.log(1 + simple_strategy_daily_return)] * len(dates)
}, index=dates)

def test_annualised_mean(synthetic_data):
    # Using known data to calculate annualised mean
    ann_mean = _calculate_ann_mean(synthetic_data, annual_periods)
    bh_ann_mean = ann_mean['Buy & Hold']
    print(f"Buy & Hold annual mean: {bh_ann_mean:.5f}")

    # Now verify correctnesss by seeing simple daily return matches simple daily return from function's independently caculated annualised      
    calculated_simple_daily_return = (1 + bh_ann_mean) ** (1 / annual_periods) - 1
    print(f"Expected simple daily return: {simple_daily_return:.5f}")
    print(f"Calculated simple daily return: {calculated_simple_daily_return:.5f}")

def test_annualised_std(synthetic_data):
    # Using known data to calculate annualised std
    ann_std = _calculate_ann_std(synthetic_data, annual_periods)
    bh_ann_std = ann_std['Buy & Hold']
    print(f"Buy & Hold annual std: {bh_ann_std:.5f}")

    # Std should be 0 since all returns are identical
    calculated_simple_daily_std = bh_ann_std / np.sqrt(annual_periods)
    expected_simple_daily_std = 0.0
    print(f"Expected simple daily std: {expected_simple_daily_std:.5f}")
    print(f"Calculated simple daily std: {calculated_simple_daily_std:.5f}")


if __name__ == "__main__":
    test_annualised_mean(synthetic_data)
    test_annualised_std(synthetic_data)