import pandas as pd
import numpy as np

import os

from toCsv import generateFileName

def vwapStrategy(feed):
    pass

def rsiStrategy(feed):
    pass

def emaStrategy(feed):
    pass

def pivotStrategy(feed):
    pass

def strategy(feed): 
    # upar wali sari strategies ka mix + don't return anything: either print the call or add a row to orders.csv file. 
    # Check its prsence before reading
    fileName= generateFileName(feed['token'], feed['symbol'])
    folder= os.path.join(os.getcwd(), 'daySummary')

    if fileName in os.listdir(folder):
        # logic 
        # read csv
        df= pd.read_csv(os.path.join(folder, fileName))
        # df mai sab kuchh hoga jo strategy lagane ke liye chahiye
        
    # pehle 5 min toh exist hi ni karegi file toh bass ignore karo
    