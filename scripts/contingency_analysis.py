import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data.preprocessing import prepare_for_log, remove_outliers_by_percentile

# Load data
data = pd.read_csv("data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv", index_col='Date', parse_dates=['Date'])
data = data[["Close", "Volume"]].copy()

# Calculate log returns
data["Return"] = data["Close"].div(data["Close"].shift(1))     # Gives return factor for that period
prepare_for_log(data["Return"])
data["Return"] = np.log(data["Return"])    

# Calculate log volume change (requires cleaning first to remove value inapplicable with log)
data['Volume'] = prepare_for_log(data['Volume'])
data['Vol_ch'] = np.log(data['Volume'].div(data['Volume'].shift(1)))

# Removing extreme outliers
data = remove_outliers_by_percentile(data, 'Vol_ch', 1, 99)
# data = data.dropna()
# upper_threshold = np.percentile(data['Vol_ch'], 99)
# lower_threshold = np.percentile(data['Vol_ch'], 1)
# data = data.loc[(data['Vol_ch'] > lower_threshold) & (data['Vol_ch'] < upper_threshold)]

# Plot the scatter
plt.scatter(x=data['Vol_ch'], y=data['Return'])
plt.xlabel("Volume Change")
plt.ylabel("Return")
plt.show()

# Discretise into bins and generate contigency heatmamp
data['Ret_cat'] = pd.qcut(data["Return"], q=10, labels=list(range(-5,0)) + list(range(1,6)))
data['Vol_cat'] = pd.qcut(data["Vol_ch"], q=10, labels=list(range(-5,0)) + list(range(1,6)))

matrix = pd.crosstab(data['Ret_cat'], data['Vol_cat'])

plt.figure(figsize=(12,8))
ax = sns.heatmap(matrix, cmap='RdYlBu_r')
ax.invert_yaxis()
plt.show()