## Backtester
Need to consider:
    - Overfitting: Need forward testing, perhaps with 80:20 split. This will be made easier when backtester is a class for reusaiblity
    - Look ahead bias: Using data from the future, e.g particularly when using percentiles

Improvements:
    - Currently Backtester.backtest_strategy just dives straight into applying the strategy, but this could maybe be broken up into small steps abstracted as different functions - for example preparing the data, which could also initialise the results attribute which the backtest_strategy appends to.
    - Currently the strategy plot prints every time (since it's called inside of the strategy), but maybe running the backtest should only print a summary of the results - and if one wants separately one can show the plot. This way, running the strategy only runs the strategy, rather than showing anything (aside from a text side effect)
    - I can avoid lookahead bias by applying the strategy only using data that would be avaiable up until that time - for example, a for loop over each data point which get the current data (current_data = data.iloc[:i+1]), which is then passed to the strategy function which returns the position - hence calculated based only off data that would have been known at that time. In this way I could make it more event-driven than vectorised calculation

## Misc Issues
    - Current performance is just guaged by multiple, particularly in optimisation - I should make this variable, such as passing an argument in to specifying which performance I want optimised on 

## Specific Design Choices
    - Strategy parameter argument must always be a dict to unamibiguously assign variable to the parameter name