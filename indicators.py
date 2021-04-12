import pandas as pd
import os
from copy import deepcopy

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

def makeReady(dic, fileName):
    path= os.path.join(os.getcwd(), 'daySummary', fileName)
    df= pd.read_csv(path)
    newDic= deepcopy(dic)
    # ----------------- logic here -----------------
    
    # -----------------logic ends ------------------
    return newDic
