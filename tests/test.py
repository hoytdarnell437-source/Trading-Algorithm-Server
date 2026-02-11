# import libraries
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

x = np.linspace(0, 150, 150, True)

# import other files
from testMACD import macd

while True:

    stockSymbol = input("Input stock symbol: ")

    data = yf.download(stockSymbol, start="2025-07-9", end="2026-02-11")
    closePrices = data["Close"][stockSymbol].tolist()
    y1 = closePrices


    fig, ax = plt.subplots()
    previousResults = 0
    previousSignal = 0
    doThis = 0
    y2 = []
    y3 = []
    i = 0

    for price in closePrices:
        # IMPORTANT action is only valid after the first ~30 iterations
        previousResults, previousSignal, action = macd(price, previousResults, previousSignal)
        print("\nResults: ", previousResults, "\nSignal: ", previousSignal, "\nAction: ", action)
        y2 += [previousResults]
        y3 += [previousSignal]

        if i > 26 and action != 0:
            doThis = action
            if action == 1:
                ax.scatter(i, price, color='red',marker='v')
            else:
                ax.scatter(i, price, color='green',marker='^')
        i += 1



    ax.plot(x, y1)
    ax.plot(x, y2)
    ax.plot(x, y3)
    plt.show()


