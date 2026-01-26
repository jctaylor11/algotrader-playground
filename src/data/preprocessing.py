import numpy as np


def prepare_for_log(series): 
    """Removes 0s, negatives, and infs, to prepare series for logarithm calculations"""
    series = series.copy()
    is_inf = np.isinf(series)
    is_zero = series == 0
    is_neg = series < 0

    # Reporting
    print(
        f"{series.name} series values replaced with NaN:\n"
        f"  {is_inf.sum()} infinities\n"
        f"  {is_zero.sum()} zeros\n"
        f"  {is_neg.sum()} negatives\n"
    )

    to_remove = is_inf | is_zero | is_neg
    series[to_remove] = np.nan

    return series


def remove_outliers_by_percentile(df, col, lower_p=1, upper_p=99):
    """Removes extreme outliers according to percentile thresholds"""
    is_na = df[col].isna()
    is_na_sum = is_na.sum()
    if is_na_sum:
        df = df.loc[~is_na]
        print(f"{is_na_sum} NaN values removed from {col} to take percentiles")
        
    lower_threshold = np.percentile(df[col], lower_p)
    upper_threshold = np.percentile(df[col], upper_p)
  
    df = df.loc[(df[col] > lower_threshold) & (df[col] < upper_threshold)]

    return df

