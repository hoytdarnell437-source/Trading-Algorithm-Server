# variables that need to be kept between calls
shares = 0
hasBought = False
def trade(price: float, capital: float, signal: int, plotObject, iteration: int):
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
    