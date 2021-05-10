from smartapi import WebSocket 
from smartapi import SmartConnect

from config import authInfo
from stockTokens import stockTokens
import dataFilter as df
import toCsv
from strategy import strategy

import json
from copy import deepcopy
import sys
import datetime as dt


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

def getHistoricData(symbol, interval, fromDate, toDate):
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
    data= df.historicDataFilter(data)
    # print comment krna hai baad mai
    print('data: \n', json.loads(data))
    # # abb isse send kar skte hain


#*********************************

feedString= ''

# interval sumary for 1 stock, there shall be a dictionary of many such dictionaries
intervalSummary= {
    'intervalStartTime': 'NA',
    'lastStrategyTime': 'NA',
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
    'currentSupport':'NA'
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


def onTick(ws, tick):
    global intervalSummary, daySummary, tokenSymbolMap

    # comment krni hai ye line
    #print('Tick: ', tick)
    for i in tick:
        for key in i:
            try:
                if key!= 'tk':
                    i[key]= float(i[key])
            except:
                continue
        print('name: ', i.get('name', 'undefined'))
        # print('tick: ', i)
        try:
                
            if i['name']== 'sf':
                  
                if not i['tk'] in daySummary:
                    temp= deepcopy(intervalSummary)
                    temp['symbol']= tokenSymbolMap[i['tk']] # example 'TATACHEM'
                    temp['token']= i['tk'] # example '3561'
                    daySummary[i['tk']]= temp
                    daySummary[i['tk']]['intervalStartTime']= roundOffTime(dt.datetime.now(), 'minute')
                    temp= {
                        'pivotpoint': 303.05,
                        's1': 301,
                        's2': 299.6,
                        's3': 297.6,
                        'r1': 305.05,
                        'r2': 306.35,
                        'r3': 308.55,
                        'ema9': 313.67,
                        'ema13': 313.21,
                        'ema26': 311.82,
                        'ema50': 309.96,
                        'currentResistance': 314,
                        'currentSupport': 308.55,
                        'vwap': 313
                    } 
                    for key in temp:
                        daySummary[i['tk']][key]= temp[key]
                    daySummary[i['tk']]['intervalStartTime']= daySummary[i['tk']]['intervalStartTime']- dt.timedelta(minutes= 5)
                    daySummary[i['tk']]['lastStrategyTime']= roundOffTime(dt.datetime.now(), 'minute')
                    print('3')    
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
                print('8')    
                # ------------- apply strategy function after 10 sec ------------------
                diff= dt.datetime.now() - daySummary[i['tk']]['lastStrategyTime']
                
                if diff.total_seconds() >= 10:
                    print('8.2')
                    strategy(daySummary[i['tk']])
                    print('8.3')
                    daySummary[i['tk']]['lastStrategyTime']= roundOffTime(dt.datetime.now(), 'second') # roundoff to latest 10 sec
                    
                print('9')                            
        except:
            
            print('some error might have occured. But nothing to worry')

def onConnect(ws, response):
    global feedString
    print('connecting')
    print(feedString)
    ws.websocket_connection()
    ws.send_request(feedString, 'mw')

def onClose(ws, code, reason):
    ws.stop()
    print('connection dropped')
    print(code)
    print(reason)
    print('-----------------trying to reconnect----------------')
    createSocketConnection(['TATAMOTORS'])

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
    
    ss.on_connect= onConnect

    ss.on_ticks= onTick

    ss.on_close= onClose

    ss.connect()
    print(feedToken)

#*****************************


# space for debugging
if __name__=='__main__':
    #apiLogin()
    #getHistoricData('TATACOMM', 'ONE_DAY', '2021-03-01 09:00', '2021-04-01 16:00')
    createSocketConnection(['TATAMOTORS'])
    
