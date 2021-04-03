import json

def socket():
    pass

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
