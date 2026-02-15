# testing implementation of the Moving Average Convergence/ Divergence algorithm

from algorithms.testEMA import ema

def macd(price: float, sensitivity: int):
    """
    Calculate MACD for given parameters intended for use inside of a loop
    
    :param price: Current price of stock
    :type price: float
    :param sensitivity: How aggressive you want the algorithm to be
    :type sensitivity: Int range 0-3
    :return: 0 is the default return 1 indicates selling is a good idea 2 indicates buying is a good idea
    :rtype: int
    """
    # macd function implementation
    global sensitivityDict, prevSignal, prevMACD
    emaFast = ema(price, "fast", sensitivityDict[str(sensitivity)][1])
    emaSlow = ema(price, "slow", sensitivityDict[str(sensitivity)][2])
    
    results = emaFast - emaSlow
    signal = ema(results, "signal", sensitivityDict[str(sensitivity)][0])


    if (prevMACD <= prevSignal) and (results > signal):
        action = 2
    elif (prevMACD >= prevSignal) and (results < signal):
        action = 1
    else:
        action = 0

    prevMACD = results
    prevSignal = signal 

    return action

sensitivityDict = {
    '0': [18, 24, 52],
    '1': [9, 12, 26],
    '2': [5, 5, 35],
    '3': [3, 5, 13]
}

prevMACD = 0.0
prevSignal = 0.0