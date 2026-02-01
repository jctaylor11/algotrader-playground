import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data.preprocessing import prepare_for_log, remove_outliers_by_percentile
from src.analysis.statistical import analyse_contingency

# Load data
data = pd.read_csv("data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv", index_col='date', parse_dates=['date'])
data = data[["close", "volume"]].copy()

# Calculate log returns
data["simple_return"] = data["close"].div(data["close"].shift(1))     # Gives return factor for that period
data["simple_return"] = prepare_for_log(data["simple_return"])
data["log_return"] = np.log(data["simple_return"])    

# Calculate log volume change (requires cleaning first to remove value inapplicable with log)
data['volume'] = prepare_for_log(data['volume'])
data['log_vol_ch'] = np.log(data['volume'].div(data['volume'].shift(1)))

# Removing extreme outliers
data = remove_outliers_by_percentile(data, 'log_vol_ch', 1, 99)

# Plot the scatter
plt.scatter(x=data['log_vol_ch'], y=data['log_return'])
plt.xlabel("Volume Change")
plt.ylabel("Return")
plt.show()

# Discretise into bins and generate contigency matrix for heatmap
matrix = analyse_contingency(data, 'log_return', 'log_vol_ch', 10)

# Show the heatmap
plt.figure(figsize=(12,8))
ax = sns.heatmap(matrix, cmap='RdYlBu_r')
ax.invert_yaxis()
plt.show()