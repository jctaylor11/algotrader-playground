import pandas as pd

def parse_ticker(payload):
    time = pd.to_datetime(payload['E'], unit='ms').strftime('%H:%M:%S')
    price = float(payload['c'])

    return time, price