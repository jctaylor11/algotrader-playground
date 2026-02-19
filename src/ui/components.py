import streamlit as st

from src.backtest.backtester_class import Backtester
from src.strategies.ma_crossover import ma_crossover_strategy


def render_ma_crossover_inputs(dataframe, start, end):   # TODO: Take previously downloaded and cached dataframe instead of filepath
    # Set inputs ranges and defaults
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


    # Optimisation section - update the session state with optimal params after found
    if st.button("Find optimal parameters"):    # This will update the optimal parameters - and if the exist, will change the display (separate block)
        bot = Backtester(
            dataframe=dataframe,
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
    
    return strategy_params
