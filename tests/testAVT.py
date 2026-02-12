def avt(high: list[float], low: list[float], close: list[float]):

    sumTR = 0
    for h, l, c in zip(high, low, close):
        sumTR += max(h - l, abs(h - c), abs(l - c))

    return sumTR / len(high)