# testing implementation of the Moving Average Convergence/ Divergence algorithm

def macd(price: float, prevMACD: float, prevSignal: float):
    # macd function implementation
    ema12 = ema(price, "ema12", 9)
    ema26 = ema(price, "ema26", 17)
    
    difference12_26 = ema12 - ema26
    results = difference12_26
    signal = ema(results, "signal", 8)

    if (prevMACD <= prevSignal) and (results > signal):
        action = 2
    elif (prevMACD >= prevSignal) and (results < signal):
        action = 1
    else:
        action = 0

    return results, signal, action # action 2 is buy, 1 is sell, 0 is neither


prevEMA = {
    "ema12": 0.0,
    "ema26": 0.0,
    "signal": 0.0
}

def ema(price: float, alphaKey: str, periods: int)->float:
    # estimated moving average function implementation
    global prevEMA
    alpha = 2 / (periods + 1) # smoothing constant

    prevEMA[alphaKey] = alpha * price + (1 - alpha) * prevEMA[alphaKey]
    return prevEMA[alphaKey]