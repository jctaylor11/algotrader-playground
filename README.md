# algotrader-playground

## Description
Repository for learning and experimenting with algorithmic bot development. This repo documents my journey in building production-ready code. 

Uses the python-binance API wrapper for accessing Binance market data.
    Documentation: https://python-binance.readthedocs.io/en/latest/market_data.html#id11 


## Project Structure
I use Jupyter Notebook for learning and exploration, distil working solutions into `/scripts`, and extract useful and reusable patterns into functions in `/src`.
 - `notebooks/` - Exploration and learning
 - `scripts/`   - Distiled work solutions from notebooks
 - `src/`       - Reusable functions and building blocks


## Workflow
1. **Download data** - Run `save_binance_ohlcv()` from `src/data/historical_data.py` to save data in data/raw_ohlcv/


