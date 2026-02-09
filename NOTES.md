## Backtester
**Need to consider:**
- Overfitting: Need forward testing, perhaps with 80:20 split. This will be made easier when backtester is a class for reusaiblity
- Look ahead bias: Using data from the future, e.g particularly when using percentiles

**Improvements:** 
- Currently Backtester.backtest_strategy just dives straight into applying the strategy, but this could maybe be broken up into small steps abstracted as different functions - for example preparing the data, which could also initialise the results attribute which the backtest_strategy appends to.
- Currently the strategy plot prints every time (since it's called inside of the strategy), but maybe running the backtest should only print a summary of the results - and if one wants separately one can show the plot. This way, running the strategy only runs the strategy, rather than showing anything (aside from a text side effect)
- I can avoid lookahead bias by applying the strategy only using data that would be avaiable up until that time - for example, a for loop over each data point which get the current data (current_data = data.iloc[:i+1]), which is then passed to the strategy function which returns the position - hence calculated based only off data that would have been known at that time. In this way I could make it more event-driven than vectorised calculation

## Performance Metrics
**Decisions**
- CAGR chosen to compare annualised returns.
$\text{CAGR} = \left( \frac{\text{Ending Equity}}{\text{Beginning Equity}} \right)^{\frac{1}{n}} - 1$
- StDev was calculated using the number of actual trading periods in the year (taken as an average over the dataset), whereas CAGR was caluclated using the full calendar year duration for the number of years. 

**Limitations**
- CAGR does not consider the volatility of trading, and assumes constant performance. 
- CAGR assumes compounding once a year.

**Volatility Calculations**
- Includes both the simple and log standard deviation calculations. Simple standard deviation is the industry standard for reporting, however log standard deviation is important for mathematical consistnecy. I have intentionally disambiguated between when simple or log values have been used, for example distinguishing between using log returns or simple returns for calculating the sharpe ratio. It seems there is contradiction in resources, considering these metrics are marketing tools - for example, using simple returns is preferable since they are higher than log, where log stdev would be preferable since it's lower than simple. 

## Misc Issues
- Current performance is just guaged by multiple, particularly in optimisation - I should make this variable, such as passing an argument in to specifying which performance I want optimised on 

## Specific Design Choices
- Strategy parameter argument must always be a dict to unamibiguously assign variable to the parameter name