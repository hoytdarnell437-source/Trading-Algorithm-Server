prevEMA = {}

def ema(price: float, i: str, periods: int)->float:
    # estimated moving average function implementation
    global prevEMA
    alpha = 2 / (periods + 1) # smoothing constant
    
    if i in prevEMA:
        prevEMA[i] = alpha * price + (1 - alpha) * prevEMA[i]
    else:
        prevEMA[i] = price

    return prevEMA[i]