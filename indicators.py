import pandas as pd
import os
from copy import deepcopy

from threading import Thread
import logging

# Logging file: ./bot.log
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='bot.log', level=logging.INFO)
logger = logging.getLogger()

def vwap(high, low, close, vol, commTotal, commVol):
    logger.info("Calculating VWAP")
    avg= (high+low+close)/3
    temp= avg*vol
    commTotal+= temp
    commVol+= vol
    vwap= commTotal/commVol
    # commTotal and commVol will be required
    # logging.info("VWAP Finished")
    return [vwap, commTotal, commVol]

def stochasticRSI(cost, low14, high14):
    logger.info("Calculating RSI")
    osc= (cost-low14)/(high14-low14)
    return osc*100

def pivotPoint(prevHigh, prevLow, prevClose,flag=1): 
    if flag=0
        logger.info("Calculating PivotPoint")
        pp= (prevClose+prevLow+prevHigh)/3

        r1= (pp*2) - prevLow
        r2= pp + (prevHigh - prevLow)
        r3= prevHigh + 2*(pp - prevLow) 

        s1= (pp*2) -prevLow
        s2= pp +(prevHigh -prevLow)
        s3= prevLow + 2*(prevHigh - pp)
        flag = 1

    data = [r3,r2,r1,pp,s1,s2,s3]     # (pivotPoint, [[Resistances],[Supports]])
    logger.info("Calculating current Support and Resistance")
    if flag = 1:
        sup = None
        res = None
        for i in data:
            if i < currPrice:
                sup = i
                break
            if i > currPrice:
                res = i
    return (sup,res)

def ema(currPrice, prevEma, n = 50):
    logger.info("Calculating EMA")
    noOfPeriods = n
    k = 2/(noOfPeriods + 1)
    emavg = K * ( currPrice - prevEma ) + prevEma   # ema = K * ( currPrice - prevEma ) + prevEma
    return emavg

def makeReady(dic, fileName):
    logger.info('Started')
    path= os.path.join(os.getcwd(), 'daySummary', fileName)
    df= pd.read_csv(path)
    newDic= deepcopy(dic)
    # ----------------- logic starts -----------------
    
    # Indicators:       vwap, pivotPoint, ema
    # resp. weightage: [.20, .40, .40] -> sum = 1
    # if sum(Strategy) > .6 : Signal Buy/Sell else: continue
    buySum = 0
    sellSum = 0
    weight = [.20, .40, .40]    # vwap, pivotPoint, ema respectively


    # vwap < currPrice -> buy
    # vwap > currPrice -> sell
    # vwap currPrice diff 3%   
    # t1 = min(1, ( [vwap -currPrice]/.03*vwap))
    # return t1* w[0]
    # currINterval [vwap][currPrice]
    t1 = min(1, ( abs(vwap -currPrice)/(.03*vwap) ) )
    if currPrice > vwap:
        buySum+= t1*w[0]
    elif currPrice < vwap:
        sellSum+= t1*w[0]



    # ema < currPrice -Buy
    # currInterval [ema][currPrice], prevInterval [ema][currPrice]

    if currInterval[currPrice] > currInterval[ema] and prevInterval[currPrice] < prevInterval[ema]:
        buySum+=w[2]
    elif currInterval[currPrice] < currInterval[ema] and prevInterval[currPrice] > prevInterval[ema]:
        sellSum+=w[2]
    elif currInterval[currPrice] > currInterval[ema]:
        buySum+=w[2]/2
    else:
        sellSum+=w[2]/2



    # pp < currPrice by .2%
     # currPrice min(R,S) -> Buy
    obj  = pivotPoint(flag=0)
    if currPrice > obj[1]:
        buySum+=w[1]
        obj = pivotPoint()
    elif currPrice < obj[0]:
        sellSum+=w[1]
        obj = pivotPoint()

    if abs(buySum - sellSum) > .5:
        if buySum > sellSum:
            pass # BUY

        else:
            pass # SELL
    else:
        pass #print data on screen(if any) and continue to next interval

    # buySum=0
    # sellSum=0


    # -----------------logic ends ------------------
    logger.info("Finished")
    return newDic

if __name__ == '__main__':
    # makeReady(dic, fileName)
    pass
