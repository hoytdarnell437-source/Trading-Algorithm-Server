# needs implementation
def aroon(price: float, period: int = 25)->int:
    """
    Docstring for aroon
    
    :param price: Price of current Iteration
    :type price: float
    :param period: Period over which to calculate the aroon
    :type period: int Defaults to 25
    :return: Buy or Sell Signal
    :rtype: int
    """
    global previousAroon

    priceList.insert(0,price)

    if len(priceList) < period:
        aroonList.append(0)
        return 0

    highIndex = 1 + priceList.index(max(priceList[:period]))
    lowIndex = 1 + priceList.index(min(priceList[:period]))

    aroonUp = 100 * (period - highIndex) / period 
    aroonDown = 100 * (period - lowIndex) / period
    aroon = aroonUp - aroonDown

    aroonList.append(aroon)
    
    if aroon >= 0 and previousAroon < 0:
        previousAroon = aroon
        return 2
    elif aroon <= 0 and previousAroon > 0:
        previousAroon = aroon
        return 1
    else:
        previousAroon = aroon
        return 0




previousAroon = 0.0
priceList = []
aroonList = [] # list that is graphed