import pandas as pd
import numpy as np

import datetime as dt
import os

from toCsv import generateFileName

def vwapStrategy(feed):
    buySum=0
    sellSum=0
    t1 = min(1, ( abs(feed['vwap'] -feed['currentPrice'])/(.03*feed['vwap']) ) )
    if feed['currentPrice'] > feed['vwap']:
        buySum+= t1*weightage['vwap']
    elif feed['currentPrice'] < feed['vwap']:
        sellSum+= t1*weightage['vwap']

    return buySum,sellSum

def rsiStrategy(feed):
    pass

def emaStrategy(feed,df,x):
    buySum=0
    sellSum=0
    if feed['currentPrice'] > currInterval['ema'+str(x)] and df.tail(1)['currentPrice'] < df.tail(1)['ema'+str(x)]:
        buySum+=weightage['ema']/4
    elif feed['currentPrice'] < currInterval['ema'+str(x)] and df.tail(1)['currentPrice'] > df.tail(1)['ema'+str(x)]:
        sellSum+=weightage['ema']/4
    elif feed['currentPrice'] > currInterval['ema'+str(x)]:
        buySum+=weightage['ema']/8
    else:
        sellSum+=weightage['ema']/8
    return buySum,sellSum


def pivotStrategy(feed):
    buySum=0
    sellSum=0
    if feed['currentPrice'] > feed['currentResistance']:
        buySum+=weightage['piv']
    elif feed['currentPrice'] < feed['currentSupport']:
        sellSum+=weightage['piv']
    return buySum,sellSum


def strategy(feed): 
    # upar wali sari strategies ka mix + don't return anything: either print the call or add a row to orders.csv file. 
    # Check its presence before reading
    fileName= generateFileName(feed['token'], feed['symbol'])
    folder= os.path.join(os.getcwd(), 'daySummary')

    # read csv
    df= pd.read_csv(os.path.join(folder, fileName))
    # df mai sab kuchh hoga jo strategy lagane ke liye chahiye

    filename = 'orders.csv'
    folder = os.path.join(os.getcwd(),'daySummary')
    
    ##############
    weightage = {
        'vwap':.2, 
        'ema': .4, 
        'piv': .4
    }
    #############

    if fileName in os.listdir(folder):
        # logic
        buySum = 0
        sellSum = 0

        vwapS = vwapStrategy(feed)
        emaS9 = emaStrategy(feed,df,9)
        emaS13 = emaStrategy(feed,df,13)
        emaS26 = emaStrategy(feed,df,26)
        emaS50 = emaStrategy(feed,df,50)
        pivotS = pivotStrategy(feed)

        buySum = vwapS[0]+emaS50[0]+emaS26[0]+emaS13[0]+emaS9[0]+pivotS[0]
        sellSum = vwapS[1]+emaS50[1]+emaS26[1]+emaS13[1]+emaS9[1]+pivotS[1]


        #############################
        if abs(buySum - sellSum) > .5:
        ##############################
            
            dct = {
            'orderPrice':feed['currentPrice']
            }

            if buySum > sellSum:
                dct['order'] = 'BUY'
                dct['stopLoss'] = 0.995*feed['currentPrice']
                dct['targetPrice'] = 1.007*feed['currentPrice']
            else:
                dct['order'] = 'SELL'
                dct['stopLoss'] = 1.005*feed['currentPrice']
                dct['targetPrice'] = 0.993*feed['currentPrice']
            dct['timeStamp'] = dt.datetime.now()

            if filename in os.listdir(folder):
                x = pd.read_csv(os.path.join(folder,filename))
                x = x.append(dct,ignore_index=True)
                x.to_csv(os.path.join(folder,filename),index=False)
            else:
                x = pd.DataFrame(columns=list(dct.keys()))
                row = [dct[i] for i in dct]
                x.loc[0]=row
                x.to_csv(os.path.join(folder,filename),index=False)

        
    # pehle 5 min toh exist hi ni karegi file toh bass ignore karo
    