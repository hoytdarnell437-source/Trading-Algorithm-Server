# variables that need to be kept between calls
shares = 0
hasBought = False
def trade(price: float, capital: float, signal: int, plotObject, iteration: int):
    """
    Handles the buying and selling processes

    :param price: price of the current iteration
    :type price: float
    :param capital: current amount of money available to purchase shares
    :type capital: float
    :param signal: Tells function whether to buy or sell
    :type signal: int (No Action: 0, Sell: 1, Buy: 2)
    :param plotObject: Used to graph actions
    :type plotObject: matplotlib graph object
    :param iteration: Used to graph actions at proper indicies
    :type iteration: int
    """
    global hasBought, shares
    if signal == 1 and hasBought: # sell
        priceChange = shares * price
        plotObject.scatter(iteration, price, color='red',marker='v')
        hasBought = False
        return priceChange
    elif signal == 2 and (not hasBought): # buy
        shares = capital / price
        plotObject.scatter(iteration, price, color='green',marker='^')
        hasBought = True
        priceChange = -(shares * price)
        return priceChange
    return 0