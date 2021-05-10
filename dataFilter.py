import json

def socket(feed, prev={}):

    try:
        # only full feed will not raise exception
        prev['currentPrice']= feed['ltp']-5
        prev['commulativeVolume']= feed['v']
        prev['buyOffers']= feed['tbq']
        prev['sellOffers']= feed['tsq']
        prev['bestBuyPrice']= feed['bp']
        prev['bestSellPrice']= feed['sp']
        prev['bestBuyVol']= feed['bq']
        prev['bestSellVol']= feed['bs']
        # prev['vwap']= feed['ap'] ........  will be updated by our own function
        prev['intervalHigh']= max(feed['ltp'], prev['intervalHigh'])
        prev['intervalLow']= min(feed['ltp'], prev['intervalLow'])
        prev['dayHigh']= max(feed['ltp'], prev['dayHigh'])
        prev['dayLow']= min(feed['ltp'], prev['dayLow'])
        prev['intervalVolume']= feed['v']-prev['intervalOpenVolume']

    except:
        print('required data missing in the tick')
        return 0
    #print('updated to:', temp)
    return prev

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

