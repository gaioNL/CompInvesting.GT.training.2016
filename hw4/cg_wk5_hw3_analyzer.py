'''
Created on Oct, 24, 2016
@author: Gaio

Portfolio analyzer

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

def readValues(valuesFile,benchmark):
    
    valuesDF = pd.read_csv(valuesFile, header=None)
    valuesDF.columns = ['year','month','day','value']
       
    #sort by increasing trade date
    valuesDF = valuesDF.sort_values(['year','month','day'])
    
    #get 1st & last date
    tradesLen = len(valuesDF) - 1
    dt_start = dt.datetime(valuesDF.iat[0,0], valuesDF.iat[0,1], valuesDF.iat[0,2],16)
    dt_end = dt.datetime(valuesDF.iat[tradesLen,0], valuesDF.iat[tradesLen,1], valuesDF.iat[tradesLen,2],16)
     
    ls_symbols = [benchmark]     
    
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
    
    return valuesDF, d_data, ldt_timestamps, dt_start , dt_end 

def analyzePerformance(benchmark,d_data,m_data,ldt_timestamps,dt_start , dt_end):
        
    #normalize array.
    na_priceMKT = m_data['actual_close'].values
    portValMKT = na_priceMKT / na_priceMKT[0]  
  
    na_price = d_data['value'].values
    portVal = na_price / na_price[0]
        
    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    dailyValMKT = portValMKT.copy()
    dailyRetMKT = tsu.returnize0(dailyValMKT)    
    
    dailyVal = portVal.copy()
    dailyRet = tsu.returnize0(dailyVal)
    
    #Calculate avgDailyReturs
    avgDailyRetMKT = np.mean(dailyRetMKT)
    avgDailyRet = np.mean(dailyRet)
    
    #calculate volatility = standard deviation of daily returns
    volMKT = np.std(dailyRetMKT)
    vol = np.std(dailyRet)
    
    #cumulative return
    cumRet=portVal[len(portVal) -1]/portVal[0]
    cumRetMKT=portValMKT[len(portValMKT) -1]/portValMKT[0]
    
    #NYSE trading days
    k = 252
    
    sharpeRatioMKT = np.sqrt(k) * (avgDailyRetMKT/volMKT)    
    sharpeRatio = np.sqrt(k) * (avgDailyRet/vol)
          
    return vol, avgDailyRet, sharpeRatio,cumRet,volMKT, avgDailyRetMKT, sharpeRatioMKT,cumRetMKT

   
def printStats(ldt_timestamps, m_data, valuesDF, dt_start,dt_end,vol, avgDailyRet, sharpeRatio,benchmark,volMKT, avgDailyRetMKT, sharpeRatioMKT,cumRet,cumRetMKT):

    #normalize protfolion & benchmark
    na_porfolio = valuesDF['value'].values
    na_normalized_portfolio = na_porfolio / na_porfolio[0]   

    na_benchmark = m_data['actual_close'].values
    na_normalized_benchmark = na_benchmark / na_benchmark[0]  
    
    print "Portfolio Performance"
    print "Start Date:", dt_start
    print "End Date:", dt_end
    print "Sharpe Ratio:", sharpeRatio
    print "Sharpe Ratio ",benchmark,":", sharpeRatioMKT
    print "Volatility (stdev of daily returns):", vol
    print "Volatility (stdev of daily returns) ",benchmark,":", volMKT
    print "Average Daily Return:", avgDailyRet
    print "Average Daily Return ",benchmark,":", avgDailyRetMKT  
    print "Cumulative Return:", cumRet
    print "Cumulative Return ",benchmark,":", cumRetMKT      
    
    plt.clf()
    plt.setp(plt.xticks()[1], rotation=30)
    plt.plot(ldt_timestamps, na_normalized_portfolio)
    plt.plot(ldt_timestamps, na_normalized_benchmark)
    plt.legend(['Portfolio', '$SPX'])
    plt.ylabel('Fund Value')
    plt.xlabel('Date')
    plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
    plt.savefig('HW3.pdf', format='pdf')    

#Main
def main(argv):
    ''' Main Function'''

    valuesFile = ''
    benchmark = ''
    
    parser = argparse.ArgumentParser()
    parser.add_argument("portfolioFile", help="Portfolio Values file")
    parser.add_argument("benchmark" ,help="Benchmark symbol")
    args = parser.parse_args()

    valuesFile = args.portfolioFile
    benchmark = args.benchmark

    valuesDF, m_data, ldt_timestamps, dt_start , dt_end= readValues(valuesFile,benchmark)

    vol, avgDailyRet, sharpeRatio,cumRet,volMKT, avgDailyRetMKT, sharpeRatioMKT,cumRetMKT = analyzePerformance(benchmark,valuesDF,m_data,ldt_timestamps,dt_start , dt_end)
      
    printStats(ldt_timestamps, m_data, valuesDF, dt_start,dt_end,vol, avgDailyRet, sharpeRatio,benchmark,volMKT, avgDailyRetMKT, sharpeRatioMKT,cumRet,cumRetMKT)
    
if __name__ == '__main__':
    main(sys.argv[1:])