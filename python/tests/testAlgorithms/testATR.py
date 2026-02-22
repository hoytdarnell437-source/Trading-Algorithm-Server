previousATR = 0.0
previousClose = 0.0
periodWarmup = 1
tr = 0.0


def atr(high: float, low: float, close: float, period: int):
    """
    Calculate the Average True Range. Meant to be called iteratively.
    
    :param high: high price
    :type high: float
    :param low: low price
    :type low: float
    :param close: close price
    :type close: float
    :param period: amount of price samples included in calculation
    :type period: int defaults to 14 
    """
    global previousATR, previousClose, periodWarmup, tr
    if previousClose > 0.0:
        tr = max(high - low, abs(high - previousClose), abs(low - previousClose))
        if periodWarmup < period:
            value = (previousATR * (periodWarmup - 1) + tr) / periodWarmup
            periodWarmup += 1
        else:
            value = (previousATR * (period - 1) + tr) / period
    else:
        value = high - low
    previousATR = value
    previousClose = close
    return value