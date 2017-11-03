'''
Created on Nov 9, 2016
@author: Gaio

Bolliger Bands

'''

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import math
import copy
import sys
from pylab import *

#
# Prepare to read the data
#
symbols = ["AAPL","MSFT"]
startday = dt.datetime(2010,4,1)
endday = dt.datetime(2010,7,31)
timeofday=dt.timedelta(hours=16)
timestamps = du.getNYSEdays(startday,endday,timeofday)

dataobj = da.DataAccess('Yahoo')
voldata = dataobj.get_data(timestamps, symbols, "volume")
adjcloses = dataobj.get_data(timestamps, symbols, "close")
actualclose = dataobj.get_data(timestamps, symbols, "actual_close")

adjcloses = adjcloses.fillna(method='ffill')
adjcloses = adjcloses.fillna(method='backfill')
adjcloses = adjcloses.fillna(1.0)

means = pd.DataFrame.rolling(adjcloses,min_periods=20,window=20,center=False).mean()

stds  = pd.DataFrame.rolling(adjcloses,min_periods=20,window=20,center=False).std()

#calculate Bolliger Bands as mean +- 1 std
bolUp   = means + stds
bolDown = means - stds

#calculate the normalized signal
bolVal = (adjcloses - means) / (stds)

#write to file
valuesFile = open( "bolNormalized.csv", "w" )
    
for row in bolVal.iterrows():
   valuesFile.writelines(str(row[0].strftime('%Y,%m,%d')) + ", " + str(row[1]['AAPL'].round(2)) + ", " +str(row[1]['MSFT'].round(2))+ "\n" )
valuesFile.close()  

# Plot the prices
plt.clf()

symtoplot = 'AAPL'
plot(adjcloses.index,means[symtoplot].values)
plot(adjcloses.index,bolUp[symtoplot].values)
plot(adjcloses.index,bolDown[symtoplot].values)
plt.legend(['Rolling Mean','Bollinger Band Up','Bollinger Band Down'])
plt.ylabel('Adjusted Close')

savefig("cg_bolliger.png", format='png')