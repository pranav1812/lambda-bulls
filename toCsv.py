from numpy import NaN
import pandas as pd 
import os # to check if a csv file with the specified name exists in day summary folder
from datetime import datetime, timedelta
import sys
import json
from indicators import makeReady
from connection import getHistoricData as gh

# dic => temporary interval summary dictionary of all selected stocks 

def generateFileName(token, symbol):
    fileName= datetime.now().strftime('%a_%d_%b_%y_')+token+'_'+symbol+'.csv'
    #print(fileName)
    return fileName

def newEntry(dic, token, symbol): # function to insert a new row into the csv
    try:
        folder= os.path.join(os.getcwd(), 'daySummary')
        fileName= generateFileName(token, symbol)
        if fileName in os.listdir(folder):
            df= pd.read_csv(os.path.join(folder, fileName))

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
                'ema50': 309.96
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
        print('either daySummary folder is missing or you ran the main file from another folder\ncd into its folder and run the file again')
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
    fileName= generateFileName('438', 'BHEL')
    print(fileName)

    print('yo')
    