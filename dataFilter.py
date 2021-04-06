import json
import indicators

def socket(feed, prev={}):
    temp= {}
    try:
        # only full feed will not raise exception
        temp['currentPrice']= feed['ltp']
        temp['commulativeVolume']= feed['vol']
        temp['buyOffers']= feed['tbq']
        temp['sellOffers']= feed['tsq']
        temp['bestBuyPrice']= feed['bp']
        temp['bestSellPrice']= feed['sp']
        temp['bestBuyVol']= feed['bq']
        temp['bestSellVol']= feed['bs']
        # indicators bhi lagane hain yahan pe
        # prev indicates dynamically made dictionary upto now
    except:
        print('required data missing in the tick')
        return 0
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
