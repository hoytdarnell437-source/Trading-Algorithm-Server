import yfinance as yf
from MACD import macd

google = yf.Ticker("GOOG")

prices = [10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10, 9, 8, 9, 10, 11, 12, 13, 14, 15]
previousResults = 0
previousSignal = 0

for price in prices:
    previousResults, previousSignal, action = macd(price, previousResults, previousSignal)
    print("\nResults: ", previousResults, "\nSignal: ", previousSignal, "\nAction: ", action)


