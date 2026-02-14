import matplotlib.pyplot as plt

from src.backtest.backtester_class import Backtester
from src.strategies.ma_crossover import ma_crossover_strategy
from src.visualisation.plot_trades import overlay_trades


# Configure backtester
filepath = 'data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv'
start = '2021-01-01'
end = '2022-02-02'

strategy_function = ma_crossover_strategy
strategy_params = {'ma_s': 50, 'ma_l': 100}
optimisation_params = {'ma_s': range(50, 100, 1), 'ma_l': range(100, 150, 1)}

# Instantiate backtester from Backtester class
bot = Backtester(
    filepath=filepath, 
    start=start, 
    end=end, 
    strategy_function=strategy_function, 
    strategy_params=strategy_params
)

# Demo of using optimisation 
optimal_strategy_params = bot.optimise_strategy_params(optimisation_params)
bot.strategy_params = optimal_strategy_params       # Updates the objects attributes with the optimal params

# Running the backtest and presenting results
bot.run_strategy_backtest()
bot.print_performance()
fig, ax = bot.plot_results()         
ax = overlay_trades(bot.get_positions(), ax)    # Overlays the trades onto the plot, using the positions
plt.show()