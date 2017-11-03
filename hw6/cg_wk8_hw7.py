'''
Created on Nov 11, 2016
@author: Gaio

'''

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import gaio_EventProfiler as ep


"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    #Gaio: considering Actual Close
    df_actual_close = d_data['actual_close']
    ts_market = df_actual_close['SPY']
    
    #calculate Bolliger Bands as mean +- 1 std
    means = pd.DataFrame.rolling(df_actual_close,min_periods=20,window=20,center=False).mean()
    stds  = pd.DataFrame.rolling(df_actual_close,min_periods=20,window=20,center=False).std()
    bolUp   = means + stds
    bolDown = means - stds
    #calculate the normalized signal
    bolVal = (df_actual_close - means) / (stds)     

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_actual_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_actual_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            
	    bolVal_today = bolVal[s_sym].ix[ldt_timestamps[i]]
	    bolVal_yest = bolVal[s_sym].ix[ldt_timestamps[i - 1]]
	    bolVal_SPY_today =bolVal['SPY'].ix[ldt_timestamps[i]]

	    # specifically, if bollinger[t-1]>=-2 & bollinger[t]<-2 && bollinger[SPY][t]>=1.4
	    if bolVal_yest >= -2 and bolVal_today < -2 and bolVal_SPY_today>=1.4 :
		df_events[s_sym].ix[ldt_timestamps[i]] = 1
                
    return df_events

def find_eventsSymTstamp(ls_symbols,ldt_timestamps):
    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    df_events = find_events(ls_symbols, d_data)    
    
    return df_events, d_data

def createOrdersFile(df_events,ldt_timestamps,outputfile):
    
    ordersFile = open( outputfile, "w" )
	
    for i in range(0,len(ldt_timestamps)):
	#Claudio
	for s_sym in df_events.columns:
	#if there is an event,then BUY 100 stocks
	    if df_events[s_sym].ix[ldt_timestamps[i]] == 1:
	    #SELL the stocks 5 days later
		dateBUY = ldt_timestamps[i]
		
		if i+5 <= len(ldt_timestamps)-1:
		    dateSELL= ldt_timestamps[i+5]
		else:
		    dateSELL= ldt_timestamps[len(ldt_timestamps)-1]

		ordersFile.writelines(dateBUY.strftime('%Y,%m,%d') + "," + str(s_sym) + ",Buy,100,\n")
		ordersFile.writelines(dateSELL.strftime('%Y,%m,%d') + "," + str(s_sym) + ",Sell,100,\n")		
	    
    ordersFile.close()     
    
    return 1

if __name__ == '__main__':
    
    outputfile='ordersEvents_10.csv'
    
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    df_events, d_data = find_eventsSymTstamp(ls_symbols,ldt_timestamps)
    
    print "Creating Study 2012"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='MyEventStudy_2012.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
    
    createOrdersFile(df_events,ldt_timestamps,outputfile)