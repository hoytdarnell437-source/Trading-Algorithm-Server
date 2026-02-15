# TODO remove loop from this function
def rsi(prices: list[float], period: int = 14):
    totalGain = 0
    totalLoss = 0
    for i in range(len(prices)):
        if i > 0:
            if prices[i] > prices[i-1]:
                totalGain += prices[i] - prices[i-1]
            else:
                totalLoss += prices[i-1] - prices[i]

    avgLoss = totalLoss / period
    avgGain = totalGain / period

    if avgLoss == 0:
        return 100.0
    
    rs = avgGain / avgLoss
    rsi = 100 - (100 / (1 + rs))

    return rsi