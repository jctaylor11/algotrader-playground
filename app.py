import streamlit as st

from src.backtest.backtester_class import Backtester
from src.strategies.ma_crossover import ma_crossover_strategy
from src.visualisation.results_plots import build_results_plotly, overlay_trades_plotly
from src.ui.components import render_ma_crossover_inputs

# Initialise sessions states
if 'run_strategy_clicked' not in st.session_state:   # For persistent button behaviour since buttons don't retain state
    st.session_state.run_strategy_clicked = False   

if 'optimal_params' not in st.session_state:
    st.session_state.optimal_params = None

# Callback function for button click event
def click_run_strategy():
    st.session_state.run_strategy_clicked = True

st.title("Algotrader")

st.divider()

# Dictionary dispatch pattern for strategy options to render input components
strategy_component_mapping = {
    "Strategy 1": render_ma_crossover_inputs,
    "Strategy 2": render_ma_crossover_inputs        # Both same strategies as placeholders - change to other strategies when added
}

# Dictionary dispatch pattern for strategy options to retrieve respective strategy function
strategy_function_mapping = {
    "Strategy 1": ma_crossover_strategy,
    "Strategy 2": ma_crossover_strategy             # Both same strategies as placeholders - change to other strategies when added
}

selected_strategy_function = None       # For variable scope
strategy_options = list(strategy_component_mapping)

# Input fields for object instantiation
left_column, right_column = st.columns(2)
start = left_column.date_input("Start date", value='2024-01-01')
end = right_column.date_input("End date", value='2025-01-01')
selected_strategy = st.selectbox('Select strategy', strategy_options, index=None)

# Filepath hardcoded for now - TODO: Parameterise with function that downloads (and caches) the data for a chosen coin 
filepath = 'data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv'

strategy_params = {}    # Initialised outside of conditional for variable scope
if selected_strategy in strategy_options:
    # Retrieves the relevant function to render UI components for the selected strategy
    render_strategy_function = strategy_component_mapping[selected_strategy]      

    # Calls function the function to render components and receive selected strategy parameters
    strategy_params = render_strategy_function(filepath=filepath, start=start, end=end)     

    # Retrieves the relevant stratgey function the the selected strategy
    selected_strategy_function = strategy_function_mapping[selected_strategy]

st.divider()

st.button("Run strategy", on_click=click_run_strategy)

# Once the button is clicked, the strategy backtest is run and results displayed
if st.session_state.run_strategy_clicked:
    try:
        # Adding the strategy params as an attribute to the object
        bot = Backtester(
            filepath=filepath,
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

        overlay_trades = st.checkbox(label="Overlay trades on chart")

        fig = build_results_plotly(results)

        if overlay_trades:
            with st.spinner('Processing trades'):
                fig = overlay_trades_plotly(results['position'], fig)

        st.plotly_chart(fig, use_container_width=False)

    except Exception as e: 
        st.error(f"Error: {str(e)}. Check your inputs") 