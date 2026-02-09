import numpy as np
import pandas as pd
import pytest

from src.reporting.performance_metrics import _calculate_cagr, _calculate_ann_simple_std


# Using a helper function instead of fixture to allow parameters to be passed in cleanly
def create_test_data(simple_returns, interval):
    """
    Creates an applicable Dataframe for performance metrics, given a list simple_returns passed in from the parametrisation
    """
    log_returns = np.log([1 + r for r in simple_returns])   # Changing simple to log once, for correct format with function

    test_data = pd.DataFrame({
        'date': pd.date_range(start='2020', periods=len(simple_returns), freq=interval),   # Not hard-coded to allow variable sample data
        'log_return': log_returns,
        'strategy_log_return': log_returns,
        'strategy_log_net': log_returns
    })
    test_data.set_index('date', inplace=True)
    return test_data


# Argument names string sets the simple_returns and expected_cagr variables, and the simple_returns is passed directly into the fixture
@pytest.mark.parametrize("simple_returns,expected_cagr,interval", [
    ([np.nan, 0.03, 0.07, 0.05, 0.12, 0.01], 0.055, "YE"),
    ([np.nan, 0.04, 0.06, 0.05, 0.06, 0.067], 0.055, "YE")
])
def test_cagr(simple_returns, expected_cagr, interval):
    """
    Tests CAGR function calculation using known values from Investopedia example

    Source: https://www.investopedia.com/terms/a/annualized-total-return.asp
    """
    # Arrange
    test_data = create_test_data(simple_returns, interval)

    #Act
    cagr = _calculate_cagr(test_data)

    print(f"Calculated CAGR: {cagr['Buy & Hold']}, Expected CAGR: {expected_cagr}")

    # Assert
    assert cagr['Buy & Hold'] == pytest.approx(expected_cagr, abs=0.001)  # Answer taken from Investpedia example, with 0.1% error


# Argument names string sets the simple_returns and expected_cagr variables, and the simple_returns is passed directly into the fixture
@pytest.mark.parametrize("simple_returns,expected_ann_std,interval", [
    ([np.nan, 0.03, 0.07, 0.05, 0.12, 0.01], 0.042, "YE"),
    ([np.nan, 0.04, 0.06, 0.05, 0.06, 0.067], 0.01, "YE")
])
def test_ann_simple_std(simple_returns, expected_ann_std, interval):
    """Tests StDev function using same Investopedia source as CAGR tests"""
    # Arrange
    test_data = create_test_data(simple_returns, interval)

    #Act
    ann_std = _calculate_ann_simple_std(test_data)

    # Assert
    print(f"Calculated Ann Std: {ann_std['Buy & Hold']}, Expected Ann Std: {expected_ann_std}")
    assert ann_std['Buy & Hold'] == pytest.approx(expected_ann_std, abs=0.001)  # Answer taken from Investpedia example, with 0.1% error