import numpy as np
import pandas as pd
import pytest

from src.reporting.performance_metrics import _calculate_cagr

# Pytest fixture to create known sample data
@pytest.fixture
def create_sample_data():
    """
    Generates the sample data using Investopedia's example.

    Source: https://www.investopedia.com/terms/a/annualized-total-return.asp
    """
    simple_returns = [np.nan, 0.04, 0.06, 0.05, 0.06, 0.067]     # 6 periods will be 5 years accounting for the starting value

    test_data = pd.DataFrame({
        'date': pd.date_range(start='2020-05-05', periods=len(simple_returns), freq=pd.DateOffset(years=1)),
        'log_return': np.log([1 + r for r in simple_returns]),
        'strategy_log_return': np.log([1 + r for r in simple_returns]),
        'strategy_log_net': np.log([1 + r for r in simple_returns])
    })
    test_data.set_index('date', inplace=True)
    return test_data

def test_cagr(create_sample_data):
    """
    Tests CAGR function calculation using known values from Investopedia example.

    Expected value: 0.055
    Source: https://www.investopedia.com/terms/a/annualized-total-return.asp
    """
    # Act
    cagr = _calculate_cagr(create_sample_data)

    # Assert
    assert cagr['Buy & Hold'] == pytest.approx(0.055, abs=0.005)  # Answer taken from Investpedia example, 0.005 abs is 2dp
