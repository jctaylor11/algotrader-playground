import streamlit as st

from src.backtest.backtester_class import Backtester
from src.strategies.ma_crossover import ma_crossover_strategy

# Setting the session state for persistent button behaviour (since the button doesn't retain state)
if 'clicked' not in st.session_state:
    st.session_state.clicked = False

# Callback function for button click event
def click_button():
    if strategy:
        st.session_state.clicked = True

st.title("Algotrader")

# List of strategies for the selectbox
strategy_options = ['Strategy 1', 'Strategy 2']

# Input fields for object instantiation
left_column, right_column = st.columns(2)
start = left_column.date_input("Start date", value='2024-01-01')
end = right_column.date_input("End date", value='2025-01-01')
strategy = st.selectbox('Select strategy', strategy_options, index=None)

# Additional input required for selected strategy
strategy_params = {}
if strategy == 'Strategy 1' or strategy == 'Strategy 2':        # For now only one strategy, but keep selection logic
    left_column, right_column = st.columns(2)
    ma_s = left_column.number_input('Parameter 1', step=10, format="%d", value=50)
    ma_l = right_column.number_input('Parameter 2', step=10, format="%d", value=100)
    strategy_params = {'ma_s': ma_s, 'ma_l': ma_l}

st.button("Run strategy", on_click=click_button)

# Filepath hardcoded for now - TODO: Parameterise with function that downloads (and caches) the data for a chosen coin 
filepath = 'data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv'

# Once the button is clicked, the strategy backtest is run and results displayed
if st.session_state.clicked == True:
    try:
        bot = Backtester(
            filepath=filepath,
            start=start,
            end=end,
            strategy_function=ma_crossover_strategy,
            strategy_params=strategy_params
        )

        # Runs the backtest and get results
        bot.run_strategy_backtest()
        performance = bot.print_performance()

        # Show the performance
        st.write(performance)
    except Exception as e: 
        st.error(f"Error: {str(e)}. Check your inputs") 
