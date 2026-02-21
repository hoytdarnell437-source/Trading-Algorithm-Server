prevEMA = {}

def ema(price: float, key: str, periods: int)->float:
    """
    Generates the Exponential Moving Average for the current price. This function is intended to be uses iteratively.
    
    :param price: Price of current iteration
    :type price: float
    :param key: key to which ema you are calculating (used to store previous ema data)
    :type key: str
    :param periods: number of price points used in calculation
    :type periods: int
    :return: Calculated Exponential Moving Average
    :rtype: float
    """
    # exponential moving average function implementation
    global prevEMA
    alpha = 2 / (periods + 1) # smoothing constant
    
    if key in prevEMA:
        prevEMA[key] = alpha * price + (1 - alpha) * prevEMA[key]
    else:
        prevEMA[key] = price

    return prevEMA[key]