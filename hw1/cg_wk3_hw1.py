'''
Created on September, 24, 2016
@author: Gaio

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

def simulate(dt_start, dt_end, ls_symbols, sy_allocations,d_data):
    
    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
    na_normalized_price = na_price / na_price[0, :]
    alloc = np.array(sy_allocations).reshape(4,1)
    
    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()

    #calculate the portfolio values
    portVal = np.dot(na_rets, alloc)
        
    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    dailyVal = portVal.copy()
    dailyRet = tsu.returnize0(dailyVal)
    
    #cumulative daily return
    cumRet = portVal[portVal.shape[0] -1][0]
    
    #Calculate avgDailyReturs
    avgDailyRet = np.mean(dailyRet)
    
    #calculate volatility = standard deviation of daily returns
    vol = np.std(dailyRet)
    
    #NYSE trading days
    k = 252
    
    sharpeRatio = np.sqrt(k) * (avgDailyRet/vol)
          
    return vol, avgDailyRet, sharpeRatio, cumRet

def optimizer(dt_start, dt_end, ls_symbols):
    
    #initial allocation
    #sy_allocations = [0.4, 0.4, 0.0, 0.2]

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    
    # Number of Trading days
    num_tradingDays = (len(ldt_timestamps))    

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))    
    
    bestAlloc = []
    sy_allocations = []
    bestSharpe = -1
    bestVol = 0.0
    bestAvgRet = 0.0
    bestCumRet = 0.0
    
    for i in range(0,11):
        for j in range(0,11-i):
            for k in range(0,11-i-j):
                for l in range(0,11-i-j-k):
                    if(i+j+k+l) == 10:
                        sy_allocations = [i/10.0,j/10.0,k/10.0,l/10.0]
                        vol, avgDailyRet, sharpeRatio, cumRet = simulate(dt_start, dt_end, ls_symbols, sy_allocations,d_data)
                        if sharpeRatio > bestSharpe:
                            bestAlloc = sy_allocations
                            bestSharpe = sharpeRatio
                            bestVol = vol
                            bestAvgRet = avgDailyRet
                            bestCumRet = cumRet                            
    
    return bestVol, bestAvgRet, bestSharpe, bestCumRet,bestAlloc
    
def printStats(dt_start,dt_end,ls_symbols,sy_allocations,vol, avgDailyRet, sharpeRatio, cumRet):

    print "Start Date:", dt_start
    print "End Date:", dt_end
    print "Symbols:", ls_symbols
    print "Optimal Allocation:", sy_allocations
    print "Sharpe Ratio:", sharpeRatio
    print "Volatility (stdev of daily returns):", vol
    print "Average Daily Return:", avgDailyRet
    print "Cumulative Return:", cumRet    

#Main
def main():
    ''' Main Function'''

    # List of symbols
    ls_symbols =       ['C', 'GS', 'IBM', 'HNZ']

    # Start and End date of the charts
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    
    vol, avgDailyRet, sharpeRatio, cumRet, sy_allocations = optimizer(dt_start, dt_end, ls_symbols)
    
    printStats(dt_start,dt_end,ls_symbols,sy_allocations,vol, avgDailyRet, sharpeRatio, cumRet)
    
if __name__ == '__main__':
    main()
