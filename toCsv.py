import pandas as pd 
import os # to check if a csv file with the specified name exists in day summary folder
from datetime import datetime
import sys

# dic => temporary interval summary dictionary of all selected stocks 

def generateFileName(token, symbol= 'unknown'):
    fileName= datetime.now().strftime('%a_%d_%b_%y_')+token+'_'+symbol+'.csv'
    #print(fileName)
    return fileName

def newEntry(dic, token, symbol= 'unknown'): # function to insert a new row into the csv
    try:
        folder= os.path.join(os.getcwd(), 'daySummary')
        fileName= generateFileName(token, symbol)
        if fileName in os.listdir(folder):
            df= pd.read_csv(os.path.join(folder, fileName))
            df= df.append(dic, ignore_index= True)
            df.to_csv(os.path.join(folder, fileName), index= False)
        else:
            df= pd.DataFrame(columns= list(dic.keys()))
            row= [dic[i] for i in dic]
            df.loc[0]= row
            df.to_csv(os.path.join(folder, fileName), index= False)
    except:
        print('either daySummary folder is missing or you ran the main file from another folder\ncd into its folder and run the file again')
        sys.exit()

if __name__=='__main__':
    # testing functions
    dic= {
        'intervalOpenTime': '10:20:00',
        'currentPrice': 1100,
        'volume': 1600045,
        'open': 1080.65,
    }
    newEntry(dic, '3721', 'TATACOM')
    dic1= {
        'intervalOpenTime': '10:25:00',
        'currentPrice': 1096.5,
        'volume': 1601545,
        'open': 1100,
    }
    newEntry(dic1, '3721', 'TATACOM')