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

def stochasticRSI(cost, low14, high14):
    osc= (cost-low14)/(high14-low14)
    return osc*100

def makeReady(dic, fileName):
    path= os.path.join(os.getcwd(), 'daySummary', fileName)
    df= pd.read_csv(path)
    # update original dictionary. so don't make copy of dic
    # ----------------- logic here -----------------
    
    # -----------------logic ends ------------------
    return dic
