'''
Created on Oct, 12, 2016
@author: Gaio

Market Simulator

'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import copy
import sys
import argparse

def readTrades(tradesFile):
    
    tradesDF = pd.read_csv(tradesFile, header=None)
    tradesDF.columns = ['year','month','day','symbol','type','qtity','price']
    
    # Get Symbols 
    ls_symbols = np.unique(list(tradesDF.iloc[:,3]))
    
    #sort by increasing trade date
    tradesDF = tradesDF.sort_values(['year','month','day'])
    
    #get 1st & last date
    tradesLen = len(tradesDF) - 1
    dt_start = dt.datetime(tradesDF.iat[0,0], tradesDF.iat[0,1], tradesDF.iat[0,2],16)
    dt_end = dt.datetime(tradesDF.iat[tradesLen,0], tradesDF.iat[tradesLen,1], tradesDF.iat[tradesLen,2],16)
    #+dt.timedelta(days=1)
    
    return tradesDF, ls_symbols, dt_start , dt_end

def readMarketPrices(ls_symbols, dt_start , dt_end):
    
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
        
    # Number of Trading days
    num_tradingDays = (len(ldt_timestamps))    
    
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')
    
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['actual_close']
    
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data)) 
    
    d_data['actual_close'] = d_data['actual_close'].fillna(method='ffill')
    d_data['actual_close'] = d_data['actual_close'].fillna(method='bfill')
    d_data['actual_close'] = d_data['actual_close'].fillna(1.0)
                    
    return ldt_timestamps,d_data

def calculatePortfolio(startCash,tradesDF,ls_symbols, dt_start , dt_end,m_data,ldt_timestamps):
    
    #create trades table
    ls_symbols = np.append(ls_symbols,'cash')
    ls_symbols = np.append(ls_symbols,'total')
    
    myTrades = pd.DataFrame(0,index=list(ldt_timestamps), columns=list(ls_symbols))   
 
    #update cash
    #loop on all trades & update the cash for each trade
    
    for i in range(0,len(tradesDF)):
        #read date, symbol & quantity
        tradeDate = dt.datetime(tradesDF.iat[i,0], tradesDF.iat[i,1], tradesDF.iat[i,2],16)
        stockSymbol = tradesDF.loc[i,'symbol']
        tradeQty = tradesDF.loc[i,'qtity']
        orderType = tradesDF.loc[i,'type']
        stockPrice = m_data['actual_close'][stockSymbol][tradeDate]
	
	#print tradeDate,stockSymbol,tradeQty,orderType,stockPrice
 
        if orderType == "Buy":
            startCash -= stockPrice * tradeQty 
            #myTrades['cash'][tradeDate] = startCash
            myTrades.loc[tradeDate:,stockSymbol] = myTrades[stockSymbol][tradeDate] + tradeQty 
        else:#Sell
            startCash += stockPrice * tradeQty  
            #myTrades['cash'][tradeDate]  = startCash
            myTrades.loc[tradeDate:,stockSymbol] = myTrades[stockSymbol][tradeDate] - tradeQty
        myTrades.loc[tradeDate:,'cash'] = startCash
	
    #update value & total
    #Claudio: print mkt prices to file
    valuesFile = open( "market_prices.csv", "w" )
    
    for tradeDate in ldt_timestamps:
	
        portValue=0
	priceStr = ''
	
        for stockSymbol in ls_symbols:
	    
            if stockSymbol == 'cash':
                
                portValue+= myTrades.loc[tradeDate,stockSymbol] 
		
            elif stockSymbol != 'total':
                stockPrice = m_data['actual_close'][stockSymbol][tradeDate]
		#Claudio: print mkt prices to file
		priceStr  = priceStr + str(m_data['actual_close'][stockSymbol][tradeDate])+','
		portValue += myTrades[stockSymbol][tradeDate] * stockPrice   
		
	#Claudio: print mkt prices to file
	valuesFile.writelines(priceStr + "\n" )	
	myTrades.loc[tradeDate,'total'] =  portValue
  
    #Claudio: print mkt prices to file
    valuesFile.close()  
	
    return myTrades

def writeOutput(myTrades,outputfile):
    
    valuesFile = open( outputfile, "w" )
    
    for row in myTrades.iterrows():
	
	valuesFile.writelines(str(row[0].strftime('%Y,%m,%d')) + ", " + str(row[1]['total'].round()) + "\n" )

    valuesFile.close()    

#Main
def main(argv):
    ''' Main Function'''

    tradesFile = ''
    outputfile = ''
    cash = 0
    
    parser = argparse.ArgumentParser()
    parser.add_argument("orderFile", help="order file")
    parser.add_argument("cash",type=int,help="cash")
    parser.add_argument("valueFile", help="output values file") 
    args = parser.parse_args()

    tradesFile = args.orderFile
    cash = args.cash
    outputfile = args.valueFile

    tradesDF, ls_symbols, dt_start , dt_end = readTrades(tradesFile)
    
    ldt_timestamps, m_data = readMarketPrices(ls_symbols, dt_start , dt_end)
    
    myTrades = calculatePortfolio(cash,tradesDF,ls_symbols, dt_start , dt_end,m_data,ldt_timestamps)
    
    writeOutput(myTrades,outputfile)
       
if __name__ == '__main__':
    main(sys.argv[1:])
