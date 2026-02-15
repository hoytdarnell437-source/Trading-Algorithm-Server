# main loop for Testing Trend Direction Methods. Currently utilizing MACD algorithm
# import libraries
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

# import other files
from algorithms.testMACD import macd
from algorithms.testRSI import rsi
from algorithms.testATR import atr
from algorithms.testTrade import trade

from helperFuncions import f20050

while True:

    # import stock data
    stockSymbol = input("Input stock symbol: ").upper()
    data = yf.download(stockSymbol, start="2024-02-11", end="2026-02-11") # CHANGE THESE DATES FOR TESTING TIMEFRAMES 
    closePrices = data["Close"][stockSymbol].tolist()
    highPrices = data["High"][stockSymbol].tolist()
    lowPrices = data["Low"][stockSymbol].tolist()


    # change these variables
    prices = closePrices
    startingCapital = 1000
    capital = 1000 # in dollars
    risk = 1 # percent
    macdSensitivity = 0

    # graphing setup
    x = np.linspace(0, len(prices), len(prices), True)
    fig, ax = plt.subplots()

    # loop variables
    totalChange = 0
    i = 0

    # main calculation loop
    for price in prices:
        # calculate macd
        action = macd(price, macdSensitivity)

        action = f20050(price)
        
        # send action to trade function
        if i > 30 and action != 0:
            capital += trade(price, capital, action, ax, i)
        elif i == (len(prices) - 1):
            capital += trade(price, capital, 1, ax, i) # ensure the stocks are sold on last iteration

        i += 1

    totalChange = capital - startingCapital

    # output data on graph and in terminal
    print("Stock: ", stockSymbol)
    print("Percent Gain in Asset Value: ", f"{(100 * totalChange / startingCapital):.2f}", "%")
    print("Percent Gain in Stock Value: ", f"{(100 * (prices[-1] - prices[0]) / prices[0]):.2f}", "%")
    ax.plot(x, prices)
    plt.show()