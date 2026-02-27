import streamlit as st
import pandas as pd

from src.backtest.backtester_class import Backtester
from src.data.historical_data import fetch_custom_binance_ohlcv, fetch_min_volume_tickers
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
if 'backtester' not in st.session_state:
    st.session_state.backtester = None


## Constants ##
PRIMARY_AVAILABLE_PAIRS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

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

    # Fetches all tickers above a threshold 24hr volume to display in coin_pair selectbox
    min_volume_for_tickers = 10000000
    all_tickers = fetch_min_volume_tickers(min_volume=min_volume_for_tickers)
    all_other_tickers = [ticker for ticker in all_tickers if ticker not in PRIMARY_AVAILABLE_PAIRS]  # To avoid duplicates
    AVAILABLE_PAIRS = PRIMARY_AVAILABLE_PAIRS + [" ━━━━━━━ "] + all_other_tickers

    # User inputs
    coin_pair = st.selectbox("Pair", options=AVAILABLE_PAIRS, help=f"Items below divider are all Binance USDT pairs  \nwith a 24 hour volume greater than ${min_volume_for_tickers:,}.")
    interval = st.selectbox("Interval", options=AVAILABLE_INTERVALS, index=3)
    start = st.date_input("Start", "2024-01-01")
    end = st.date_input("End", "2025-01-01")

    if st.button("Load Data", width="stretch"):
        if start > end: 
            st.error("Start must be before end")
        elif coin_pair not in all_tickers:
            st.error("Select a valid coin pair")
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

        if selected_strategy in strategy_options:
            # Retrieves selected strategy's function to render UI components 
            render_strategy_function = STRATEGY_MAPPING[selected_strategy]["component"]  

            # Renders strategy's UI components and receives selected parameters
            strategy_params = render_strategy_function(dataframe=st.session_state.custom_data, start=start, end=end)     

            # Retrieves selected stratgey's logic function
            selected_strategy_function = STRATEGY_MAPPING[selected_strategy]["function"]

        if selected_strategy and st.button("Run Backtest", type="primary", width="stretch"):
            st.session_state.run_strategy_clicked = True
            st.session_state.strategy_params = strategy_params

            try:
                # Instantiates backtester, runs the test, and stores the object
                backtester = Backtester(
                    dataframe=st.session_state.custom_data,
                    start=start,
                    end=end,
                    strategy_function=selected_strategy_function,       
                    strategy_params=strategy_params
                )
                backtester.run_strategy_backtest()
                st.session_state.backtester = backtester

            except Exception as e: 
                st.error(f"Error: {str(e)}. Check your inputs") 

else:
    st.info("Select and load data from the sidebar to begin")

if st.session_state.run_strategy_clicked:
    st.divider()
    st.subheader("Performance")

    with st.container():
        # Runs the backtest and get results
        performance_metrics = st.session_state.backtester.performance_metrics
        results = st.session_state.backtester.results

        print(performance_metrics)
        print(results)

        total_return = performance_metrics.loc["Strategy", "Total Return"]
        benchmark_return = performance_metrics.loc["Buy & Hold", "Total Return"]
        excess_return = total_return - benchmark_return

        # Formatting the metrics for significant figures to display
        display_metrics = performance_metrics.copy()
        for col in display_metrics.columns:
            if col in ('CAGR', 'Total Return'):
                display_metrics[col] = display_metrics[col].map("{:.0%}".format)
            else:
                display_metrics[col] = display_metrics[col].map("{:.2f}".format)

        # List of tuples for display in format (label, value, delta, help message)
        metrics_to_display = [
            ("Total Return",     display_metrics.loc["Strategy", "Total Return"], f"{excess_return:.0%}", "Total Return excluding fees (for now).  \nDelta shows excess return against benchmark."),
            ("Benchmark Return", display_metrics.loc["Buy & Hold", "Total Return"], "",                   "Buy & Hold used as benchmark"),
            ("Volatility",       display_metrics.loc["Strategy", "Ann StDev"],    "",                     ""),
            ("Sharpe Ratio",     display_metrics.loc["Strategy", "Sharpe Ratio"], "",                     "")
        ]

        # CAGR only displays if greater than a year - 400 days to avoid 'approx 1 year' rounding with 10% 
        display_cagr = (end - start).days > 400
        if display_cagr:
            metrics_to_display.insert(2, ("CAGR", display_metrics.loc["Strategy Net", "CAGR"], "", ""))

        # Displays each metric in display_metric in columns
        for col, (label, value, delta, help) in zip(st.columns(len(metrics_to_display)), metrics_to_display):
            col.metric(label, value, delta=delta, help=help)
        
        st.divider()

        fig = build_results_plotly(results)

        overlay_trades = st.checkbox(label="Overlay trades on chart")

        if overlay_trades:
            with st.spinner('Processing trades', show_time=True):
                fig = overlay_trades_plotly(results['position'], fig)

        st.plotly_chart(fig, width="stretch")

        # Show the performance
        if display_cagr:
            st.dataframe(display_metrics)
        else:
            st.dataframe(display_metrics.drop(columns="CAGR"))


