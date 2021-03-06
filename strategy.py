import pandas as pd
import numpy as np

import datetime as dt
import os

from toCsv import generateFileName

def vwapStrategy(feed, weightage):
    buySum=0
    sellSum=0
    t1 = min(1, ( abs(feed['vwap'] -feed['currentPrice'])/(.03*feed['vwap']) ) )
    if feed['currentPrice'] > feed['vwap'] and feed['lastStrategyPrice']< feed['vwap']:
        buySum+= t1*weightage['vwap']
    elif feed['currentPrice'] < feed['vwap'] and feed['lastStrategyPrice']> feed['vwap']:
        sellSum+= t1*weightage['vwap']

    return buySum,sellSum

def emaStrategy(feed,x, weightage):
    buySum=0
    sellSum=0
    if feed['currentPrice'] > feed['ema'+str(x)] and feed['lastStrategyPrice'] < feed['ema'+str(x)]:
        buySum+=weightage['ema']/4
    elif feed['currentPrice'] < feed['ema'+str(x)] and feed['lastStrategyPrice'] > feed['ema'+str(x)]:
        sellSum+=weightage['ema']/4
    elif feed['currentPrice'] > feed['ema'+str(x)]:
        buySum+=weightage['ema']/8
    else:
        sellSum+=weightage['ema']/8
    return buySum,sellSum


def pivotStrategy(feed, weightage):
    arr= [feed['s3'], feed['s2'], feed['s1'], feed['pivotpoint'], feed['r1'], feed['r2'], feed['r3']]
    buySum=0
    sellSum=0
    if feed['currentPrice'] > feed['currentResistance'] and feed['lastStrategyPrice']< feed['currentResistance']:
        buySum+=weightage['piv']
        feed['currentSupport']= feed['currentResistance']
        try:
            feed['currentResistance']= arr[arr.index(feed['currentResistance']) +1]
        except:
            ################################################
            feed['currentResistance']= feed['currentResistance']*1.02
            ################################################
    elif feed['currentPrice'] < feed['currentSupport'] and feed['lastStrategyPrice']> feed['currentSupport']:
        sellSum+=weightage['piv']
        feed['currentResistance']= feed['currentSupport']
        try:
            feed['currentSupport']= arr[arr.index(feed['currentSupport']) -1]
        except:
            ################################################
            feed['currentSupport']= feed['currentSupport']*0.98
            ################################################
    return buySum,sellSum


def strategy(feed): 
    # upar wali sari strategies ka mix + don't return anything: either print the call or add a row to orders.csv file. 
    # Check its presence before reading
    # print('input: ',feed)
    
    if dt.datetime.now().hour >9 or dt.datetime.now().minute > 30: # 9:30 se pehle koi trade nahi leni
        if feed['lastStrategyPrice']== 'NA':
            feed['lastStrategyPrice']= feed['currentPrice']


        # # read csv
        # df= pd.read_csv(os.path.join(folder, fileName))
        # # df mai sab kuchh hoga jo strategy lagane ke liye chahiye

        filename = 'orders.csv'
        folder = os.path.join(os.getcwd(),'daySummary')
        
        ##############
        weightage = {
            'vwap':.2, 
            'ema': .4, 
            'piv': .4
        }
        #############
        print('8.2.1')
        
        buySum = 0
        sellSum = 0
        # print('8.2.2')
        vwapS = vwapStrategy(feed, weightage)
        # print('8.2.3')
        emaS9 = emaStrategy(feed,9, weightage)
        # print('8.2.4')

        emaS13 = emaStrategy(feed, 13, weightage)
        # print('8.2.5')

        emaS26 = emaStrategy(feed, 26, weightage)
        # print('8.2.6')

        emaS50 = emaStrategy(feed, 50, weightage)
        

        pivotS = pivotStrategy(feed,  weightage)
        

        buySum = vwapS[0]+emaS50[0]+emaS26[0]+emaS13[0]+emaS9[0]+pivotS[0]
        sellSum = vwapS[1]+emaS50[1]+emaS26[1]+emaS13[1]+emaS9[1]+pivotS[1]
        

        print('diff', abs(buySum - sellSum))
        #############################
        if abs(buySum - sellSum) > .15:
        ##############################
            print('reached')
            dct = {
                'orderPrice':feed['currentPrice'],
                'symbol': feed['symbol']
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
                print('appending row')
                x = pd.read_csv(os.path.join(folder,filename))
                x = x.append(dct,ignore_index=True)
                x.to_csv(os.path.join(folder,filename),index=False)
                print('appended row')
            else:
                x = pd.DataFrame(columns=list(dct.keys()))
                row = [dct[i] for i in dct]
                x.loc[0]=row
                x.to_csv(os.path.join(folder,filename),index=False)

    # finally lastStrategyPrice ko update krdo
    feed['lastStrategyPrice']= feed['currentPrice']
    print('.', end= ' ')
