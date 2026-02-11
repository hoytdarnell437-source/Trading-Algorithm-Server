# import libraries
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

x = np.linspace(0, 150, 150, True)

# import other files
from testMACD import macd

#google = yf.Ticker("GOOG")
#data = google.history()

data = yf.download("GOOG", start="2025-07-9", end="2026-02-11")
df = data["Close"]["GOOG"].tolist()
closePrices = list(df)
y1 = closePrices

previousResults = 0
previousSignal = 0
i = 0

for price in closePrices:
    # IMPORTANT action is only valid after the first ~30 iterations
    previousResults, previousSignal, action = macd(price, previousResults, previousSignal)
    print("\nResults: ", previousResults, "\nSignal: ", previousSignal, "\nAction: ", action)
    if i > 26 and action != 0:
        
    i += 1



fig, ax = plt.subplots()
ax.plot(x, y1, label="Cos")
#ax.plot(x, y2, label="sin")
plt.show()


