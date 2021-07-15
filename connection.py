from smartapi import SmartWebSocket as WebSocket 
from smartapi import SmartConnect

from config import authInfo
from stockTokens import stockTokens
import dataFilter as df
import toCsv
from strategy import strategy
from indicators import preparePastData

import json
from copy import deepcopy
import sys
import datetime as dt
import numpy as np
import pandas as pd
import os


def apiLogin():
    smartApi= SmartConnect(api_key= authInfo['apiKey'])

    login= smartApi.generateSession(authInfo['clientCode'], authInfo['password'])
    refreshToken= login['data']['refreshToken']
    feedToken= smartApi.getfeedToken()
    #profile= smartApi.getProfile(refreshToken)

    # print('login jwt token: ', login['data']['jwtToken'])
    # print('auth may be: ', smartApi.Authorization)
    smartApi.generateToken(refreshToken)
    
    print("successfully logged in")
    print('ft', feedToken)
    return {
        'login': login,
        'feedToken': feedToken,
        'apiObj': smartApi
    }

def convertTimeStamp(timestampString):
    l= timestampString.split('T')
    date, time= l[0], l[1]
    timestampString= date + ' ' + time.split('+')[0]
    
    return dt.datetime.strptime(timestampString, '%Y-%m-%d %H:%M:%S') 

def getHistoricData(symbol, interval, fromDate, toDate): # (fromDate is exclusive, toDate is inclusive)
    # agar boht sara data aane wala hai toh usse chunks mai call krna, ie. period ko parts mai break krna aur parallely pichhle wale ko operate krna
    apiLoginObj= apiLogin()
    apiObj= apiLoginObj['apiObj']
    try:
        tkn= stockTokens[symbol]
    except:
        print('wrong stock symbol maybe, check stocksTokens.py for reference')
        sys.exit()
    
    reqObj= {
    'exchange': 'NSE',
    'symboltoken': tkn,
    'interval': interval,
    'fromdate': fromDate,
    'todate': toDate
    }

    res= apiObj.getCandleData(reqObj)

    
    # data= json.loads(r.text)
    
    if res['message']!= 'SUCCESS':
        print('connection error occurred, try again 2-3 times')
        sys.exit()
    
    data= res['data']
    print('successfully connected to historical api')
    # data= df.historicDataFilter(data)
    # print comment krna hai baad mai
    for i in range(len(data)):
        data[i][0]= convertTimeStamp(data[i][0])
    
    return data
    # # abb isse send kar skte hain

def getDateRange():
    # Format: '2021-05-20 16:00'
    # past 15 days is enough
    a= dt.timedelta(days= 15)
    x= dt.datetime.now()
    y= x - a

    return str(y.date()) + ' 09:00', str(x.date()) + ' 09:00'

def prepareStockData(symbol):
    date1, date2= getDateRange()
    try:
        tkn= stockTokens[symbol]
    except:
        print('wrong stock symbol maybe, check stocksTokens.py for reference')
        sys.exit()
    print(date1, date2)
    # '2021-06-24 09:15', '2021-07-09 09:15'
    data= getHistoricData(symbol, 'FIVE_MINUTE', date1, date2)
    data= np.array(data)
    tempDic= {}
    columns= ['intervalStartTime', 'intervalOpen', 'intervalHigh', 'intervalLow', 'currentPrice', 'intervalVolume']
    for i, key in enumerate(columns):
        temp= []
        for j in data:
            temp.append(j[i])
        tempDic[key]= temp
    df= pd.DataFrame(tempDic)
    df= preparePastData(df, tkn, symbol)
    df.to_csv(os.path.join(os.getcwd(), 'daySummary', 'tatamotor.csv'), index= False)
    
    

#*********************************

feedString= ''

# interval sumary for 1 stock, there shall be a dictionary of many such dictionaries
intervalSummary= {
    'intervalStartTime': 'NA',
    'lastStrategyTime': 'NA',
    'lastStrategyPrice': 'NA',
    'symbol': 'NA',
    'token': 'NA',
    'currentPrice':'NA',
    'intervalOpen': 'NA',
    'intervalHigh': float('-inf'),
    'intervalLow': float('inf'),
    'dayHigh': float('-inf'),
    'dayLow': float('inf'),
    'buyOffers': 'NA',
    'sellOffers': 'NA',
    'bestBuyPrice': 'NA',
    'bestSellPrice': 'NA',
    'bestBuyVol': 'NA',
    'bestSellVol': 'NA',
    'vwap': 'NA',
    'intervalVolume': 0,
    'commulativeVolume': 0,
    'intervalOpenVolume': 0,
    'commulativeTotal': 0,
    'ema50':'NA',
    'ema9':'NA',
    'ema13':'NA',
    'ema26':'NA',
    'currentResistance':'NA',
    'currentSupport':'NA',
    'pivotpoint': 'NA',
    'r1': 'NA',
    'r2': 'NA',
    'r3': 'NA',
    's1': 'NA',
    's2': 'NA',
    's3': 'NA'
}



tokenSymbolMap= {} # reverse of stocktokens dictionary

daySummary= {} #  dictionary of interval summaries of all stocks in consideration

def roundOffTime(x, gap):
    y= ''
    if gap=='minute':
        y= dt.datetime(x.year, x.month, x.day, x.hour, 5*(x.minute//5) , 0, 0)
    elif gap=='second':
        y= dt.datetime(x.year, x.month, x.day, x.hour, x.minute, 10* (x.second//10), 0)
    else:
        print('unidentified gap value for roundoffTime function')
        sys.exit()
    return y

def temp(ws, message):
    print(message)

def onTick(ws, tick):
    global intervalSummary, daySummary, tokenSymbolMap
    # comment krni hai ye line
    print('Tick: ', tick)
    for i in tick:
        for key in i:
            try:
                if key!= 'tk':
                    i[key]= float(i[key])
            except:
                continue
        
        ##############################
        print('name: ', i.get('name', 'undefined'), end= ' -> ')
        # print('tick: ', i)
        try:
                
            if i.get('name', 'undefined')== 'sf':
                    
                if not i['tk'] in daySummary:
                    temp= deepcopy(intervalSummary)
                    temp['symbol']= tokenSymbolMap[i['tk']] # example 'TATACHEM'
                    temp['token']= i['tk'] # example '3561'
                    daySummary[i['tk']]= temp
                    daySummary[i['tk']]['intervalStartTime']= roundOffTime(dt.datetime.now(), 'minute')
                    daySummary[i['tk']]['intervalOpen']= i['ltp']
                    daySummary[i['tk']]['intervalStartTime']= daySummary[i['tk']]['intervalStartTime']
                    daySummary[i['tk']]['lastStrategyTime']= roundOffTime(dt.datetime.now(), 'minute')
                        
                x= df.socket(i, daySummary[i['tk']])
                    
                if x!=0:
                    daySummary[i['tk']]= x
                    


                # ------------- save to CSV after 5 minutes------------------
                diff= dt.datetime.now() - daySummary[i['tk']]['intervalStartTime'] 
                    
                if diff.total_seconds() >= 5*60: # 5 mins
                    toCsv.newEntry(daySummary[i['tk']], i['tk'], daySummary[i['tk']]['symbol'])
                        
                    # -----------------------------------------------------------------------------

                    daySummary[i['tk']]['intervalStartTime']= roundOffTime(dt.datetime.now(), 'minute') # roundoff to latest 5 min
                    
                    # -----------------------------------------------------------------------------
                    daySummary[i['tk']]['intervalOpen']=  daySummary[i['tk']]['currentPrice']
                    daySummary[i['tk']]['intervalHigh']= daySummary[i['tk']]['currentPrice']
                    daySummary[i['tk']]['intervalLow']= daySummary[i['tk']]['currentPrice']
                    daySummary[i['tk']]['intervalVolume']= 0
                    daySummary[i['tk']]['intervalOpenVolume']= daySummary[i['tk']]['commulativeVolume']
                    
                # ------------- apply strategy function after 10 sec ------------------
                diff= dt.datetime.now() - daySummary[i['tk']]['lastStrategyTime']
                
                if diff.total_seconds() >= 10:
                    
                    strategy(daySummary[i['tk']])
                    
                    daySummary[i['tk']]['lastStrategyTime']= roundOffTime(dt.datetime.now(), 'second') # roundoff to latest 10 sec
                
            
                
                                        
        except:
            
            print('some error might have occured. But nothing to worry')

def onConnect(ws):
    global feedString
    print('connecting')
    print(feedString)
    # ws.websocket_connection()
    ws.subscribe('mw', "nse_cm|2885&nse_cm|1594&nse_cm|11536")

def onClose(ws):
    print("connection closed!!")

def onError(ws, error):
    print('ERROR OCCURRED\n--------------')
    print(error, '\n------------')

def createSocketConnection(symbols):
    feedToken= apiLogin()['feedToken']
    print('ft2', feedToken)
    tokenList= []
    
    global tokenSymbolMap
    for i in symbols:
        if i in stockTokens:
            tokenSymbolMap[stockTokens[i]]= i # eg. '3461': 'TATACHEM'
            tokenList.append('nse_cm|'+stockTokens[i])
        else:
            print('{} is not a recognized symbol, check stockTokens.py for reference\ntry again'.format(i))
            sys.exit()

    global feedString

    feedString= '&'.join(tokenList)
    print(feedString)
    
    
    ss= WebSocket(feedToken, authInfo['clientCode'])
    
    ss._on_open= onConnect

    # ss._on_message= onTick
    ss._on_message= temp

    ss._on_error= onError

    ss._on_close= onClose

    ss.connect()
    print(feedToken)

#*****************************


# space for debugging
if __name__=='__main__':
    #apiLogin()
    prepareStockData('TATAMOTORS')
    # stockList= ['TATAMOTORS', 'RELIANCE']
    # createSocketConnection(stockList)
    
