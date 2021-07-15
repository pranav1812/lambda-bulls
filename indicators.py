import pandas as pd
import os
import sys


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
    # logger.info("Calculating EMA")
    noOfPeriods = n
    k = 2/(noOfPeriods + 1)
    emavg = k * ( currPrice - prevEma ) + prevEma   # ema = K * ( currPrice - prevEma ) + prevEma
    return emavg

############# Average for ADX #############
def smooth(curr, prev, period):
    return prev - (prev / period) + curr


def adx(df, dic):
    plusDM1= dic['intervalHigh'] - df['intervalHigh'].iloc[-1]
    minusDM1= df['intervalLow'].iloc[-1] - dic['intervalLow']
    plusDM= 0
    minusDM= 0
    if plusDM1> minusDM1:
        plusDM= max(0, plusDM1)
    else:
        minusDM= max(0, minusDM1)
    a= dic['intervalHigh'] - dic['intervalLow']
    b= abs(dic['intervalHigh'] - df['currentPrice'].iloc[-1])
    c= abs(dic['intervalLow'] - df['currentPrice'].iloc[-1])
    trueRange= max(a, b, c)

    # data would be pepared first

    ##### Replace EMA with smooth ######
    prevTrueRangeEMA= df['trueRange14'].iloc[-1] # assuming it to be present
    trueRange14= smooth(trueRange, prevTrueRangeEMA, 14)

    plusDI14= df['plusDM14'].iloc[-1]
    minusDI14= df['plusDM14'].iloc[-1]


    plusDI14= smooth(plusDM, plusDI14, 14)
    minusDI14= smooth(minusDM, minusDI14, 14)

    dx= 100 * (abs(plusDI14 - minusDI14) / (plusDI14 + minusDI14))
    adxVal= (sum(df['adx'].iloc[ - 14: -1]) + dx) / 14
    return trueRange, trueRange14, plusDM, minusDM, plusDI14, minusDI14, dx, adxVal






def makeReady(dic, fileName):
    path= os.path.join(os.getcwd(), 'daySummary', fileName)
    df= pd.read_csv(path)
    # update original dictionary. so don't make copy of dic
    # ----------------- logic here -----------------
    obj = vwap(dic['intervalHigh'],dic['intervalLow'],dic['currentPrice'],dic['intervalVolume'],dic['commulativeTotal'],dic['commulativeVolume'])
    dic['commulativeTotal'] = obj[1]
    dic['vwap'] = obj[0]

    dic['ema50'] = ema(dic['currentPrice'],df['ema50'].iloc[-1], 50)
    dic['ema13'] = ema(dic['currentPrice'],df['ema13'].iloc[-1], 13)
    dic['ema9']  = ema(dic['currentPrice'],df['ema9'].iloc[-1], 9)
    dic['ema26'] = ema(dic['currentPrice'],df['ema26'].iloc[-1], 26)


    dic['trueRange'], dic['trueRange14'], dic['plusDM'], dic['minusDM'], dic['plusDM14'], dic['minusDM14'], dic['dx'], dic['adx']= adx(df.tail(2), dic)
   
    # -----------------logic ends ------------------
    return dic

def preparePastData(df, token, symbol):
    defaultColumns= ['vwap', 'lastStrategyTime', 'dayHigh', 'dayLow', 'r1', 'r2', 'r3', 
    's1', 's2', 's3', 'pivotpoint', 'currentResistance', 'currentSupport']
    
    for col in defaultColumns:
        df[col]= -1
    df['token']= token
    df['symbol']= symbol

    emas= ['ema9', 'ema13', 'ema26', 'ema50']
    emaPeriods= [9, 13, 26, 50]
    initialEmas= []

    for i in range(4):
        x= emaPeriods[i]
        em= [-1 for i in range(x-1)]
        em.append(df['currentPrice'].iloc[:x].sum() / x)

        initialEmas.append(em) 
    
    # try:
    for x, i in enumerate(initialEmas):
        for j in range(len(i), len(df)):
            i.append(ema(df['currentPrice'].iloc[j], i[-1], emaPeriods[x]))
    # except:
    #     print(error)
    #     print(df.columns.values.tolist ())
    #     sys.exit()

    for ind, colName in enumerate(emas):
        df[colName]= initialEmas[ind]
   
    # adx calculations
    trueRange= [-1]
    plusDM= [-1]
    minusDM= [-1]
    for i in range(1, len(df)):
        plusDM1= df['intervalHigh'].iloc[i] - df['intervalHigh'].iloc[i-1]
        minusDM1= df['intervalLow'].iloc[i-1] - df['intervalLow'].iloc[i]
        
        if plusDM1> minusDM1:
            plusDM.append(max(0, plusDM1))
            minusDM.append(0)
        else:
            minusDM.append(max(0, minusDM1))
            plusDM.append(0)
        a= df['intervalHigh'].iloc[i] - df['intervalLow'].iloc[i]
        b= abs(df['intervalHigh'].iloc[i] - df['currentPrice'].iloc[i-1])
        c= abs(df['intervalLow'].iloc[i] - df['currentPrice'].iloc[i-1])
        trueRange.append(max(a, b, c))
    
    plusDM14= []
    minusDM14= []
    dx= []
    trueRange14= []

    for i in range(14):
        plusDM14.append(-1)
        minusDM14.append(-1)
        dx.append(-1)
        trueRange14.append(-1)
    plusDM14.append(sum(plusDM[1 : 15]))
    minusDM14.append(sum(minusDM[1 : 15]))
    trueRange14.append(sum(trueRange[1 : 15]))
    d= (plusDM14[-1] - minusDM14[-1]) / (plusDM14[-1] + minusDM14[-1])
    dx.append(abs(d)*100)
    for i in range(15, len(df)):
        plusDM14.append(smooth(plusDM[i], plusDM14[-1], 14))
        minusDM14.append(smooth(minusDM[i], minusDM14[-1], 14))
        trueRange14.append(smooth(trueRange[i], trueRange14[-1], 14))
        d= (plusDM14[-1] - minusDM14[-1]) / (plusDM14[-1] + minusDM14[-1])
        dx.append(abs(d)*100)
    
    adxArr= []
    for i in range(29):
        adxArr.append(-1)
    for i in range(29, len(df)):
        adxArr.append(sum(dx[ i-13 : i+1]) / 14)

       
    df['trueRange']= trueRange
    df['trueRange14']= trueRange14
    df['plusDM']= plusDM
    df['minusDM']= minusDM
    df['plusDM14']= plusDM14
    df['minusDM14']= minusDM14
    df['dx']= dx
    df['adx']= adxArr

    return df







    
    
    
    


    
    