import streamlit as st
import plotly.graph_objects as go

from src.backtest.backtester_class import Backtester
from src.strategies.ma_crossover import ma_crossover_strategy
from src.visualisation.results_plots import build_results_plotly, overlay_trades_plotly
from src.ui.components import render_ma_crossover_inputs

# Initialise sessions states
if 'run_strategy_clicked' not in st.session_state:   # For persistent button behaviour since buttons don't retain state
    st.session_state.run_strategy_clicked = False   

if 'optimal_params' not in st.session_state:
    st.session_state.optimal_params = None

if 'overlay_trades' not in st.session_state:
    st.session_state.overlay_trades = False

# Callback function for button click event
def click_run_strategy():
    st.session_state.run_strategy_clicked = True

st.title("Algotrader")

st.divider()

# List of strategies for the selectbox
strategy_options = ['Strategy 1', 'Strategy 2']

# Input fields for object instantiation
left_column, right_column = st.columns(2)
start = left_column.date_input("Start date", value='2024-01-01')
end = right_column.date_input("End date", value='2025-01-01')
strategy = st.selectbox('Select strategy', strategy_options, index=None)

# Filepath hardcoded for now - TODO: Parameterise with function that downloads (and caches) the data for a chosen coin 
filepath = 'data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv'

# Additional input required for selected strategy
strategy_params = {}    # Outside the conditional for variable scope
if strategy == 'Strategy 1' or strategy == 'Strategy 2':        # For now only one strategy, but keep selection logic
    strategy_params = render_ma_crossover_inputs(filepath, start, end)


st.divider()
st.button("Run strategy", on_click=click_run_strategy)

# Once the button is clicked, the strategy backtest is run and results displayed
if st.session_state.run_strategy_clicked == True:
    try:
        # Adding the strategy parmas as an attribute to the object
        bot = Backtester(
            filepath=filepath,
            start=start,
            end=end,
            strategy_function=ma_crossover_strategy,
            strategy_params=strategy_params
        )

        # Runs the backtest and get results
        bot.run_strategy_backtest()
        performance_table = bot.print_performance()
        results = bot.get_results()

        # Show the performance
        st.write(performance_table)

        overlay_trades = st.checkbox(label="Overlay trades on chart")

        fig = build_results_plotly(results)

        if overlay_trades:
            with st.spinner('Processing trades'):
                fig = overlay_trades_plotly(results['position'], fig)

        st.plotly_chart(fig, use_container_width=False)

    except Exception as e: 
        st.error(f"Error: {str(e)}. Check your inputs") 