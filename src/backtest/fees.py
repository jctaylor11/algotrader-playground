import numpy as np

def apply_trading_commissions(data, commission):
    data = data.copy()
    log_commission_multiplier = np.log(1 - commission)        # Add to strategy_log_return to get net return per trade after fees
    data['trade'] = data['position'].diff().fillna(0).abs()         
    data['strategy_log_net'] = data['strategy_log_return'] + (data['trade'] * log_commission_multiplier)
    data['cum_strategy_net'] = np.exp(data['strategy_log_net'].cumsum())

    return data