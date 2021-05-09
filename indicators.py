import pandas as pd
import os


# Note: Shayad RSI theek se code ni ho payega. Iski requirements discuss kar lenge


def vwap(high, low, close, vol, commTotal, commVol):
    avg= (high+low+close)/3
    temp= avg*vol
    commTotal+= temp
    commVol+= vol
    vwap= commTotal/commVol
    # commTotal and commVol will be required
    return [vwap, commTotal, commVol]

def ema(currPrice, prevEma, n ):
    logger.info("Calculating EMA")
    noOfPeriods = n
    k = 2/(noOfPeriods + 1)
    emavg = K * ( currPrice - prevEma ) + prevEma   # ema = K * ( currPrice - prevEma ) + prevEma
    return emavg

def makeReady(dic, fileName):
    path= os.path.join(os.getcwd(), 'daySummary', fileName)
    df= pd.read_csv(path)
    # update original dictionary. so don't make copy of dic
    # ----------------- logic here -----------------
    obj = vwap(dic['intervalHigh'],dic['intervalLow'],dic['currentPrice'],dic['intervalVolume'],dic['commulativeTotal'],dic['commulativeVolume'])
    dic['commulativeTotal'] = obj[1]
    dic['vwap'] = obj[0]

    dic['ema50'] = ema(dic['currentPrice'],dic['ema50'],50)
    dic['ema13'] = ema(dic['currentPrice'],dic['ema13'],13)
    dic['ema9']  = ema(dic['currentPrice'],dic['ema9'],9)
    dic['ema26'] = ema(dic['currentPrice'],dic['ema26'],26)


    
    # -----------------logic ends ------------------
    return dic
