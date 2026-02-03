from src.backtest.backtester_class import Backtester
from src.strategies.ma_crossover import ma_crossover_strategy

# Configure backtester
filepath = 'data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv'
start = '2021-01-01'
end = '2022-02-02'
strategy_function = ma_crossover_strategy
strategy_params = [50, 100]

# Instantiate backtester from Backtester class
bot = Backtester(
    filepath=filepath, 
    start=start, 
    end=end, 
    strategy_function=strategy_function, 
    strategy_params=strategy_params
)

bot.run_strategy_backtest()
bot.print_performance()
bot.plot_results()