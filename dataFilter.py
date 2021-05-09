import json
import indicators

def socket(feed, prev={}):
    temp= {}
    try:
        # only full feed will not raise exception
        temp['currentPrice']= feed['ltp']
        temp['symbol']= prev['symbol'],
        temp['commulativeVolume']= feed['v']
        temp['buyOffers']= feed['tbq']
        temp['sellOffers']= feed['tsq']
        temp['bestBuyPrice']= feed['bp']
        temp['bestSellPrice']= feed['sp']
        temp['bestBuyVol']= feed['bq']
        temp['bestSellVol']= feed['bs']
        temp['vwap']= feed['ap']
        temp['intervalHigh']= max(feed['ltp'], prev['intervalHigh'])
        temp['intervalLow']= min(feed['ltp'], prev['intervalLow'])
        temp['dayHigh']= max(feed['ltp'], prev['dayHigh'])
        temp['dayLow']= min(feed['ltp'], prev['dayLow'])
        temp['intervalVolume']= feed['v']-prev['intervalOpenVolume']
        temp['intervalOpenVolume']= prev['intervalOpenVolume']
        temp['intervalStartTime']= prev['intervalStartTime']

        # indicators bhi lagane hain yahan pe
        # prev indicates dynamically made dictionary upto now
    except:
        print('required data missing in the tick')
        return 0
    #print('updated to:', temp)
    return temp

def historicDataFilter(data):
    # data is in the form of string
    # data will be called in chunks from the api
    dataList= data.split('\n')
    for i in range(len(dataList)):
        vals= dataList[i].split(',')
        obj= {
            'time': vals[0],
            'open': vals[1],
            'high': vals[2],
            'low': vals[3],
            'close': vals[4],
            'volume': vals[5]
        }
        dataList[i]= json.dumps(obj)
    return json.dumps(dataList)

