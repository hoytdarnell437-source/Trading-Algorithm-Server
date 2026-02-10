import yfinance as yf
import pandas as pd
from MACD import macd

google = yf.Ticker("GOOG")
data = google.history()
df = pd.DataFrame(data)
closePrices = df["Close"].tolist()

previousResults = 0
previousSignal = 0

for price in closePrices:
    # IMPORTANT action is only valid after the first ~30 iterations
    previousResults, previousSignal, action = macd(price, previousResults, previousSignal)
    print("\nResults: ", previousResults, "\nSignal: ", previousSignal, "\nAction: ", action)


