from algorithms.EMA import ema

prevEma50 = 0.0
prevEma200 = 0.0
initialLow = 0.0
intermediaryHigh = 0.0
lowBroken = False
prevPrices = []

def f20050(price: float):
    global prevEma200, prevEma50, initialLow, intermediaryHigh, lowBroken
    ema50 = ema(price, "50", 50)
    ema200 = ema(price, "200", 200)
    # begin buy bias
    if ema50 >= ema200 and prevEma50 < prevEma200:
        prevEma50 = ema50
        prevEma200 = ema200
        return 2
    # begin sell bias
    elif ema50 <= ema200 and prevEma50 > prevEma200:
        prevEma50 = ema50
        prevEma200 = ema200
        return 1
    else:
        prevEma50 = ema50
        prevEma200 = ema200
        return 0