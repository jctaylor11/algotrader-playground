# algotrader-playground

## Description
Repository for learning and experimenting with algorithmic trading development. 
Used for development of two core systems: EV Engine and Backtest Engine. 

Uses the python-binance API wrapper for accessing Binance market data.
    Documentation: https://python-binance.readthedocs.io/en/latest/market_data.html

## Project Structure
 - `notebooks/` - Jupyter Notebooks for experimentation and exploration. 
 - `scripts/`   - Scripts for database, analysis, and backtest. 
 - `src/`       - Reusable functions and building blocks.
 - `app.py`     - Streamlit application for strategy backtest visualisation. 

## EV Engine
Evaluates the expected value for a parameterised 'fingerprint' of market state, based on historical market data.
Indicators will be tested for statistical significance before inclusion. 
Intended for expansion with higher-value exogenous data sources, though currently developed around endogenous indicators.

## Backtest Engine
Framework for developing and validating trading strategies against historical data, with performance metrics including Sharpe Ratio.
