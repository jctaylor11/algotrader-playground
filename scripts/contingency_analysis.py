import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data.preprocessing import prepare_for_log, remove_outliers_by_percentile
from src.analysis.statistical import analyse_contingency

# Load data
data = pd.read_csv("data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv", index_col='Date', parse_dates=['Date'])
data = data[["Close", "Volume"]].copy()

# Calculate log returns
data["Return"] = data["Close"].div(data["Close"].shift(1))     # Gives return factor for that period
data["Return"] = prepare_for_log(data["Return"])
data["Return"] = np.log(data["Return"])    

# Calculate log volume change (requires cleaning first to remove value inapplicable with log)
data['Volume'] = prepare_for_log(data['Volume'])
data['Vol_ch'] = np.log(data['Volume'].div(data['Volume'].shift(1)))

# Removing extreme outliers
data = remove_outliers_by_percentile(data, 'Vol_ch', 1, 99)

# Plot the scatter
plt.scatter(x=data['Vol_ch'], y=data['Return'])
plt.xlabel("Volume Change")
plt.ylabel("Return")
plt.show()

# Discretise into bins and generate contigency matrix for heatmap
matrix = analyse_contingency(data, 'Return', 'Vol_ch', 10)

# Show the heatmap
plt.figure(figsize=(12,8))
ax = sns.heatmap(matrix, cmap='RdYlBu_r')
ax.invert_yaxis()
plt.show()