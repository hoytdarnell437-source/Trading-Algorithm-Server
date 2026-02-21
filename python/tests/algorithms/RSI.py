# testing implementation of the Relative Strength Index Algorithm
def rsi(price: float, period: int = 14):
    """
    Calculate the Relative Strength Index. Meant to be called iteratively.
    
    :param price: price of the current day
    :type price: float
    :param period: amount of price samples included in calculation
    :type period: int defaults to 14 
    """
    global priceCount,prevPrice, prevAvgLoss, prevAvgGain
    gain = 0
    loss = 0

    priceCount += 1

    if priceCount == 1:
        prevPrice = price
        rsiList.append(0)
        return 0

    change = price - prevPrice
    prevPrice = price

    if change > 0:
        gain = change
    else:
        loss = -change

    avgModifier = 1/period

    avgLoss = avgModifier * loss + (1 - avgModifier) * prevAvgLoss
    avgGain = avgModifier * gain + (1 - avgModifier) * prevAvgGain

    prevAvgLoss = avgLoss
    prevAvgGain = avgGain

    if priceCount <= period:
        rsiList.append(0)
        return 0

    if avgLoss == 0:
        rsi = 100.0
    else:
        rs = avgGain / avgLoss
        rsi = 100 - (100 / (1 + rs))
    
    rsiList.append(rsi)

    if rsi < 30:
        return 2
    elif rsi > 70:
        return 1
    else:
        return 0

priceCount = 0
prevPrice = 0.0
prevAvgLoss = 0.0
prevAvgGain = 0.0
rsiList = []