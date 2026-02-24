import streamlit as st
import pandas as pd

from src.backtest.backtester_class import Backtester
from src.data.historical_data import fetch_custom_binance_ohlcv
from src.strategies.ma_crossover import ma_crossover_strategy
from src.ui.components import render_ma_crossover_inputs
from src.visualisation.results_plots import build_results_plotly, overlay_trades_plotly


def progress_cb(current_progress):
    print(f"Current progress: {current_progress}")
    if current_progress < 100:
        loading_bar.progress(current_progress)
    else:
        loading_bar.empty()

## Configuration ## 
st.set_page_config(page_title="Algotrader", layout="wide")

## Session state initialisation ##
if 'custom_data' not in st.session_state:
    st.session_state.custom_data = None
if 'optimal_params' not in st.session_state:
    st.session_state.optimal_params = None
if 'run_strategy_clicked' not in st.session_state:   # Since buttons don't retain state
    st.session_state.run_strategy_clicked = False  

## Constants ##
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

## Side bar inputs ## 
with st.sidebar:
    st.header("Data Input")

    coin_pair = st.selectbox("Pair", options=AVAILABLE_PAIRS)
    interval = st.selectbox("Interval", options=AVAILABLE_INTERVALS, index=3)
    start = st.date_input("Start", "2024-01-01")
    end = st.date_input("End", "2025-01-01")

    if st.button("Load Data", width="stretch"):
        if start > end: 
            st.Error("Start must be before end")
        else:
            loading_bar = st.progress(0, "Loading")
            try:
                custom_data = fetch_custom_binance_ohlcv(coin_pair, interval, str(start), str(end), progress_cb)

                if custom_data is not None and not custom_data.empty: 
                    st.session_state.custom_data = custom_data
                    st.session_state.custom_data_info = {
                        "Pair": coin_pair,
                        "Interval": interval,
                        "Start": str(start),
                        "End": str(end),
                        "Rows": str(len(custom_data))   # All values are strings for compatibility with Streamlit's PyArrow
                    }
                else:
                    st.error("No data found")
            except Exception as e:
                st.error(f"Failed to load data: {str(e)}")


    if st.session_state.custom_data is not None: 
        st.success(f"Loaded")

        custom_data_info = pd.Series(st.session_state.custom_data_info, name="Loaded Data")
        st.dataframe(custom_data_info)

## Main area ##
st.title("Algotrader")

if st.session_state.custom_data is not None:
    st.subheader("Strategy")

    with st.container(border=True):

        strategy_options = list(STRATEGY_MAPPING)
        selected_strategy = st.selectbox(label="Select Strategy", options=strategy_options, index=None)

        strategy_params = {}    # Initialised outside of conditional for variable scope
        if selected_strategy in strategy_options:
            # Retrieves selected strategy's function to render UI components 
            render_strategy_function = STRATEGY_MAPPING[selected_strategy]["component"]  

            # Renders strategy's UI components and receives selected parameters
            strategy_params = render_strategy_function(dataframe=st.session_state.custom_data, start=start, end=end)     

            # Retrieves selected stratgey's logic function
            selected_strategy_function = STRATEGY_MAPPING[selected_strategy]["function"]

    if selected_strategy and st.button("Run Backtest", type="primary", width="stretch"):
            st.session_state.run_strategy_clicked = True

else:
    st.info("Select and load data from the sidebar to begin")

if st.session_state.run_strategy_clicked:
    st.divider()
    st.subheader("Performance")

    with st.container():
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
            performance_metrics = bot.performance_metrics
            results = bot.results

            # Formatting the metrics for significant figures to display
            for col in performance_metrics.columns:
                if col in ('CAGR', 'Total Return'):
                    performance_metrics[col] = performance_metrics[col].map("{:.0%}".format)
                else:
                    performance_metrics[col] = performance_metrics[col].map("{:.2f}".format)

            # if (end - start).days > 400:
            #     col_1, col_2, col_3, col_4, col_5 = st.columns(5)
            #     col_1.metric("Total Return", performance_metrics.loc["Strategy Net", "Total Return"])
            #     col_2.metric("Benchmark Return", performance_metrics.loc["Buy & Hold", "Total Return"])
            #     col_3.metric("CAGR", performance_metrics.loc["Strategy Net", "CAGR"])
            #     col_4.metric("Sharpe Ratio", performance_metrics.loc["Strategy Net", "Sharpe Ratio"])
            #     col_5.metric("Volatility", performance_metrics.loc["Strategy Net", "Ann StDev"])
            # else:
            #     col_1, col_2, col_3, col_4 = st.columns(4)
            #     col_1.metric("Total Return", performance_metrics.loc["Strategy Net", "Total Return"])
            #     col_2.metric("Benchmark Return", performance_metrics.loc["Buy & Hold", "Total Return"])
            #     col_3.metric("Sharpe Ratio", performance_metrics.loc["Strategy Net", "Sharpe Ratio"])
            #     col_4.metric("Volatility", performance_metrics.loc["Strategy Net", "Ann StDev"])

            metrics_to_display = [
            ("Total Return",     performance_metrics.loc["Strategy Net", "Total Return"]),
            ("Benchmark Return", performance_metrics.loc["Buy & Hold",   "Total Return"]),
            ("Sharpe Ratio",     performance_metrics.loc["Strategy Net", "Sharpe Ratio"]),
            ("Volatility",       performance_metrics.loc["Strategy Net", "Ann StDev"]),
            ]

            # CAGR only displays if greater than a year - 400 days to avoid 'approx 1 year' rounding with 10% 
            display_cagr = (end - start).days > 400
            if display_cagr:
                metrics_to_display.insert(2, ("CAGR", performance_metrics.loc["Strategy Net", "CAGR"]))

            # Displays each metric in display_metric in columns
            for col, (label, value) in zip(st.columns(len(metrics_to_display)), metrics_to_display):
                col.metric(label, value)
            
            st.divider()

            fig = build_results_plotly(results)

            overlay_trades = st.checkbox(label="Overlay trades on chart")

            if overlay_trades:
                with st.spinner('Processing trades', show_time=True):
                    fig = overlay_trades_plotly(results['position'], fig)

            st.plotly_chart(fig, width="stretch")

            # Show the performance
            if display_cagr:
                st.dataframe(performance_metrics)
            else:
                st.dataframe(performance_metrics.drop(columns="CAGR"))

            print(bot.performance_metrics)

        except Exception as e: 
            st.error(f"Error: {str(e)}. Check your inputs") 


