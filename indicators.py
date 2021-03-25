def vwap(high, low, close, vol, commTotal, commVol):
    avg= (high+low+close)/3
    temp= avg*vol
    commTotal+= temp
    commVol+= vol
    vwap= commTotal/commVol
    # commTotal and commVol will be required
    return [vwap, commTotal, commVol]

def stochasticRSI(cost, low14, high14):
    osc= (cost-low14)/(high14-low14)
    return osc*100


