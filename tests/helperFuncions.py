from algorithms.testEMA import ema

prevEma50 = 0.0
prevEma200 = 0.0

def f20050(price: float):
    global prevEma200, prevEma50
    ema50 = ema(price, "50", 50)
    ema200 = ema(price, "200", 200)
    if ema50 >= ema200 and prevEma50 < prevEma200:
        prevEma50 = ema50
        prevEma200 = ema200
        return 2
    elif ema50 <= ema200 and prevEma50 > prevEma200:
        prevEma50 = ema50
        prevEma200 = ema200
        return 1
    else:
        prevEma50 = ema50
        prevEma200 = ema200
        return 0