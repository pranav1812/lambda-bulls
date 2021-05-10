from numpy import NaN
import pandas as pd 
import os # to check if a csv file with the specified name exists in day summary folder
from datetime import datetime, timedelta
import sys
import json
from indicators import makeReady
# from connection import getHistoricData as gh

# dic => temporary interval summary dictionary of all selected stocks 

def generateFileName(token, symbol, date= datetime.now()):
    # fileName= date.strftime('%a_%d_%b_%y_')+token+'_'+symbol+'.csv'

    fileName= symbol+'_'+token+'.csv' # not making day wise files
    #print(fileName)
    return fileName

def newEntry(dic, token, symbol): # function to insert a new row into the csv
    try:
        folder= os.path.join(os.getcwd(), 'daySummary')
        fileName= generateFileName(token, symbol)
        if fileName in os.listdir(folder):
            df= pd.read_csv(os.path.join(folder, fileName))

            if dic['vwap']== 'NA': # matlab initial indicators nahi aaye hue
                dic['vwap']= df['vwap'].iloc[-1]
                dic['ema9']= df['ema9'].iloc[-1]
                dic['ema13']= df['ema9'].iloc[-1]
                dic['ema26']= df['ema26'].iloc[-1]
                dic['ema50']= df['ema50'].iloc[-1]

                x= {
                    'h': df['dayHigh'].iloc[-1],
                    'l': df['dayLow'].iloc[-1],
                    'c': df['currentPrice'].iloc[-1]
                }
                p= (x['h']+x['l']+x['c']) / 3
                dic['pivotpoint']= p
                dic['r1']= 2*p - x['l']
                dic['r2']= p + (x['h'] - x['l'])
                dic['r3']= p + 2*(x['h'] - x['l'])
                dic['s1']= 2*p - x['h']
                dic['s2']= p - (x['h'] - x['l'])
                dic['s3']= p - 2*(x['h'] - x['l'])

            arr= [dic['s1'], dic['s2'], dic['s3'], dic['pivotpoint'], dic['r1'], dic['r2'], dic['r3']]

            # finding current resistance and support. These are also revised in strategy function whenever broken 

            for i in arr:
                if i> dic['currentPrice']:
                    dic['currentResistance']= i
            for i in range(len(arr)-1, -1):
                if i< dic['currentPrice']:
                    dic['currentSupport']= i


            # ------------- making the new entry ready, by inserting indicators ----------------
            newDic= makeReady(dic, fileName)
            # original dictionary bhi update karni hai. By default pass by reference hi hota hai
            
            df= df.append(newDic, ignore_index= True)
            df.to_csv(os.path.join(folder, fileName), index= False)
        else:
            # call required data from node API and store the response to a dictionary called temp 

            # ----------------------------- Historical API se data nikalne ke liye --------------------------- 
            # def formatDate(x):
            #     mnt= ''
            #     if x.month< 10:
            #         mnt= '0'+str(x.month)
            #     else:
            #         mnt= str(x.month)
            #     day= ''
            #     if x.day< 10:
            #         day= '0'+str(x.day)
            #     else:
            #         day= str(x.day)
            #     return str(x.year)+ '-'+ mnt + '-'+ day 

            # x= datetime.now()
            # y= timedelta(days= 2)
            # fromDate= formatDate(x) + ' 09:00'
            # toDate= formatDate(x-y) + ' 04:00'
            # data= gh(dic['symbol'], 'ONE_DAY', fromDate, toDate) 
            # -----------------------------------------------
            prevCsv= generateFileName(dic['token'], dic['symbol'], datetime.now()-timedelta(days= 2))
            print('reading previous file')
            a= pd.read_csv(os.path.join(os.getcwd(), 'daySummary', prevCsv))

            temp= {
                'pivotpoint': a['pivotpoint'].iloc[-1],
                's1': a['s1'].iloc[-1],
                's2': a['s2'].iloc[-1],
                's3': a['s3'].iloc[-1],
                'r1': a['r1'].iloc[-1],
                'r2': a['r2'].iloc[-1],
                'r3': a['r3'].iloc[-1],
                'ema9': a['ema9'].iloc[-1],
                'ema13': a['ema13'].iloc[-1],
                'ema26': a['ema26'].iloc[-1],
                'ema50': a['ema50'].iloc[-1]
            } # would be response from api. includes 1st vwap, pivot, 3 supports, 3 resistances, ema (13, 26, 50) 

            # #################################################

            # copy response dictionary to original dictionary. Called once per day for every share
            for key in temp:
                dic[key]= temp[key]

            df= pd.DataFrame(columns= list(dic.keys()))
            row= [dic[i] for i in dic]
            
            df.loc[0]= row
            df.to_csv(os.path.join(folder, fileName), index= False)
    except:
        print('either daySummary folder is missing or previous day file was not present or you ran the main file from another folder\ncd into its folder and run the file again')
        sys.exit()

if __name__=='__main__':
    # testing functions
    # dic= {
    #     'intervalOpenTime': '10:20:00',
    #     'currentPrice': 1100,
    #     'volume': 1600045,
    #     'open': 1080.65,
    # }
    # newEntry(dic, '3721', 'TATACOM')
    # dic1= {
    #     'intervalOpenTime': '10:25:00',
    #     'currentPrice': 1096.5,
    #     'volume': 1601545,
    #     'open': 1100,
    # }
    # newEntry(dic1, '3721', 'TATACOM')
    fileName= generateFileName('3456', 'TATAMOTORS')
    print(fileName)

    print('yo')
    