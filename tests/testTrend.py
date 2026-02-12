# import libraries
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

# import other files
from testMACD import macd
from testRSI import rsi
from testATR import atr
from testTrade import trade

while True:

    stockSymbol = input("Input stock symbol: ")

    data = yf.download(stockSymbol, start="2024-02-11", end="2026-02-11") # CHANGE THESE DATES FOR TESTING TIMEFRAMES 
    closePrices = data["Close"][stockSymbol].tolist()
    highPrices = data["High"][stockSymbol].tolist()
    lowPrices = data["Low"][stockSymbol].tolist()


    # change these variables
    prices = closePrices
    startingCapital = 1000
    capital = 1000 # in dollars
    risk = 1 # percent
    macdSensitivity = 3

    x = np.linspace(0, len(prices), len(prices), True)
    fig, ax = plt.subplots()

    startPrice = prices[0]
    totalChange = 0
    atrResults = 1
    high = 0
    y2 = []
    y3 = []

    i = 0
    for price in prices:
        # calculate macd
        action = macd(price, macdSensitivity)
        riskPerTrade = capital * risk * 0.01
        
        # send action to trade function
        if i > 30 and action != 0:
            capital += trade(price, capital + totalChange, action, ax, i)

        i += 1

    totalChange = capital - startingCapital

    print("Stock: ", stockSymbol)
    print("Percent Gain in Asset Value: ", f"{(100 * totalChange / startingCapital):.2f}", "%")
    print("Percent Gain in Stock Value: ", f"{(100 * (prices[-1] - startPrice) / startPrice):.2f}", "%")
    ax.plot(x, prices)
    plt.show()