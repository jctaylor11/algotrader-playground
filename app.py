import streamlit as st
import plotly.graph_objects as go

from src.backtest.backtester_class import Backtester
from src.strategies.ma_crossover import ma_crossover_strategy

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
    ma_s_min = 5
    ma_s_max = 100
    ma_s_default = 20
    ma_l_min = 10
    ma_l_max = 200
    ma_l_default = 50

    # The default values are either set defaults, or the optimal parameters if they exist
    optimal_params = st.session_state.optimal_params
    ma_s_set = optimal_params["ma_s"] if optimal_params is not None else ma_s_default
    ma_l_set = optimal_params["ma_l"] if optimal_params is not None else ma_l_default

    # Set the sliders and update strategy params 
    ma_s = st.slider("MA_S", ma_s_min, ma_s_max, value=ma_s_set)
    ma_l = st.slider("MA_L", ma_l_min, ma_l_max, value=ma_l_set)
    strategy_params = {'ma_s': ma_s, 'ma_l': ma_l}

    # Filepath hardcoded for now - TODO: Parameterise with function that downloads (and caches) the data for a chosen coin 
    filepath = 'data/raw_ohlcv/BTCUSDT-1h-2017-08-17.csv'

    # Optimisation section - update the session state with optimal params after found
    if st.button("Find optimal parameters"):    # This will update the optimal parameters - and if the exist, will change the display (separate block)
        bot = Backtester(
            filepath=filepath,
            start=start,
            end=end,
            strategy_function=ma_crossover_strategy,
        )

        with st.spinner("Computing optimal parameters", show_time=True):
            optimals = bot.optimise_strategy_params({"ma_s": range(ma_s_min, ma_s_max, 1), "ma_l": range(ma_l_min, ma_l_max, 1)})   # PARAMS RANGE DICT GOES AS AN ARGUMENT - taken from slider range
        st.session_state.optimal_params = optimals
        st.rerun()

    if st.session_state.optimal_params:
        st.success(f"Optimal strategy parameters in sample are {optimal_params['ma_s']} and {optimal_params['ma_l']}")

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

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=results.index,
            y=(results['cum_return']-1)*100,    # Converts multiplier to %
            name='Benchmark (Buy & Hold)',
            line=dict(color='blue', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=results.index,
            y=(results['cum_strategy']-1)*100,
            name='Strategy',
            line=dict(color='red', width=2, dash='dash')
        ))

        fig.update_layout(
            height=500,
            width=800,
            xaxis=dict(title='Date'),
            yaxis=dict(title='Performance', ticksuffix='%'),
            hovermode='x unified',
            legend=dict(x=0.02, y=1.01, bgcolor='rgba(255,255,255,0)'),    # Setting the last to 0 so it's transparent),
            margin=dict(t=20)
            )

        st.plotly_chart(fig, use_container_width=False)
    
    except Exception as e: 
        st.error(f"Error: {str(e)}. Check your inputs") 