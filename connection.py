from smartapi import WebSocket 
from smartapi import SmartConnect

from config import authInfo
from stockTokens import stockTokens
import dataFilter as df

import json
import requests as req
import sys


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
    return {
        'login': login,
        'feedToken': feedToken
    }

def getHistoricData(symbol, interval, fromDate, toDate):
    # agar boht sara data aane wala hai toh usse chunks mai call krna, ie. period ko parts mai break krna aur parallely pichhle wale ko operate krna
    login= apiLogin()['login']
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

    url= 'https://apiconnect.angelbroking.com/rest/secure/angelbroking/historical/v1/getCandleData'

    headers= {
        'X-PrivateKey': authInfo['apiKey'], 
        'Accept': 'application/json', 
        'X-SourceID': 'WEB', 
        'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
        'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
        'X-MACAddress': 'MAC_ADDRESS',
        'X-UserType': 'USER', 
        'Authorization': login['data']['jwtToken'], 
        'Content-Type': 'application/json'
    }
    r= req.post(url, data= json.dumps(reqObj), headers= headers)
    
    # print('encoding: ', r.encoding)
    data= json.loads(r.text)
    
    while data['message']!= 'SUCCESS':
        print('connection error occurred, try again 2-3 times')
        sys.exit()
    print('successfully connected to historical api')
    data= df.historicDataFilter(data['data'])
    # print comment krna hai baad mai
    print('data: \n', json.loads(data)[0])
    # abb isse send kar skte hain


#*********************************

feedString= ''
daySummary= {
    'currentPrice':'NA',
    'commulativeVolume': 'NA',
    'buyOffers': 'NA',
    'sellOffers': 'NA',
    'bestBuyPrice': 'NA',
    'bestSellPrice': 'NA',
    'bestBuyVol': 'NA',
    'bestSellVol': 'NA'
}

def onTick(ws, tick):
    global daySummary
    print('Ticks: ', tick)
    for i in tick:
        try:
            if i['name']== 'sf':
                if df.socket(i, daySummary[i['tk']])!=0:
                    daySummary[i['tk']]= df.socket(i, daySummary[i['tk']])
        except:
            print('some error might have occured. But nothing to worry')

def onConnect(ws, response):
    global feedString
    print('connecting')
    ws.send_request(feedString, 'mw')

def onClose(ws, code, reason):
    ws.stop()
    print('connection dropped')
    print(code)
    print(reason)

def createSocketConnection(symbols):
    feedToken= apiLogin()['feedToken']
    
    tokenList= []
    
    for i in symbols:
        if i in stockTokens:
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
    getHistoricData('TATACOMM', 'ONE_DAY', '2021-03-01 09:00', '2021-04-01 16:00')
    createSocketConnection(['TATACOMM', 'TATAMOTORS', 'TATAPOWER'])
