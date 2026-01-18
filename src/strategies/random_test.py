def random_test_strategy(price):
    if (int(price) % 3 == 0):
        return ("BUY")
    elif (int(price) % 11 == 0):
        return ("SELL")
    else: 
        return ("HOLD")