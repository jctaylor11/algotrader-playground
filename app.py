import streamlit as st

from src.backtest.backtester_class import Backtester
from src.strategies.ma_crossover import ma_crossover_strategy
from src.visualisation.results_plots import build_results_plotly, overlay_trades_plotly
from src.ui.components import render_ma_crossover_inputs
from src.data.historical_data import fetch_custom_binance_ohlcv

def progress_cb(current_progress):
    print(f"IN Funciton: {current_progress}")
    if current_progress < 100:
        loading_bar.progress(current_progress)
    else:
        loading_bar.empty()


# Configure constants
AVAILABLE_PAIRS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

AVAILABLE_INTERVALS = ['1w', '1d', '4h', '1h']

STRATEGY_MAPPING = {
    "Strategy 1": {
        "component": render_ma_crossover_inputs,
        "function": ma_crossover_strategy
    },
    "Strategy 2": {
        "component": render_ma_crossover_inputs,
        "function": ma_crossover_strategy
    }
}

# Initialise sessions states
if 'run_strategy_clicked' not in st.session_state:   # For persistent button behaviour since buttons don't retain state
    st.session_state.run_strategy_clicked = False   

if 'optimal_params' not in st.session_state:
    st.session_state.optimal_params = None

if 'custom_data' not in st.session_state:
    st.session_state.custom_data = None

# Callback function for button click event
def click_run_strategy():
    st.session_state.run_strategy_clicked = True

st.title("Algotrader")
st.divider()

strategy_options = list(STRATEGY_MAPPING)
selected_strategy_function = None   # For variable scope

# Input fields for object instantiation
left_column, right_column = st.columns(2)
coin_pair = left_column.selectbox('Pair', AVAILABLE_PAIRS)
interval = right_column.selectbox('Interval', AVAILABLE_INTERVALS, index=1)
left_column, right_column = st.columns(2)
start = left_column.date_input("Start date", value='2024-01-01')
end = right_column.date_input("End date", value='2025-01-01')

if st.button("Load data"):
    loading_bar = st.progress(0, "loading")

    st.session_state.custom_data = fetch_custom_binance_ohlcv(coin_pair, interval, str(start), str(end), progress_cb)

    # with st.spinner("Loading data", show_time=True):
    #     st.session_state.custom_data = fetch_custom_binance_ohlcv(coin_pair, interval, str(start), str(end), progress)

if st.session_state.custom_data is not None and not st.session_state.custom_data.empty:
    st.success("Loaded")

st.divider()
selected_strategy = st.selectbox('Select strategy', strategy_options, index=None)

# Filepath hardcoded for now - TODO: Parameterise with function that downloads (and caches) the data for a chosen coin 
# filepath = 'data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv'

strategy_params = {}    # Initialised outside of conditional for variable scope
if selected_strategy in strategy_options:
    # Retrieves the relevant function to render UI components for the selected strategy
    render_strategy_function = STRATEGY_MAPPING[selected_strategy]["component"]  

    # Calls function the function to render components and receive selected strategy parameters
    strategy_params = render_strategy_function(dataframe=st.session_state.custom_data, start=start, end=end)     

    # Retrieves the relevant stratgey function the the selected strategy
    selected_strategy_function = STRATEGY_MAPPING[selected_strategy]["function"]

st.divider()

st.button("Run strategy", on_click=click_run_strategy)

# Once the button is clicked, the strategy backtest is run and results displayed
if st.session_state.run_strategy_clicked:
    try:
        # Adding the strategy params as an attribute to the object
        bot = Backtester(
            dataframe=st.session_state.custom_data,
            start=start,
            end=end,
            strategy_function=selected_strategy_function,       
            strategy_params=strategy_params
        )

        # Runs the backtest and get results
        bot.run_strategy_backtest()
        performance_table = bot.print_performance()
        results = bot.get_results()

        # Show the performance
        st.write(performance_table)

        fig = build_results_plotly(results)

        overlay_trades = st.checkbox(label="Overlay trades on chart")

        if overlay_trades:
            with st.spinner('Processing trades'):
                fig = overlay_trades_plotly(results['position'], fig)

        st.plotly_chart(fig, use_container_width=False)

    except Exception as e: 
        st.error(f"Error: {str(e)}. Check your inputs") 