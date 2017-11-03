'''
Created on Jan 16, 2013
Fixed Oct 9, 2016

@author: Gaio
@contact: sourabh@sourabhbajaj.com
@summary: EventProfiler

'''

import numpy as np
import matplotlib.pyplot as plt

import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.qsdateutil as du


def eventprofiler(df_events_arg, d_data, i_lookback=20, i_lookforward=20,
                s_filename='study', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY'):
    ''' Event Profiler for an event matix'''
    df_close = d_data['close'].copy()
    df_rets = df_close.copy()

    # Do not modify the original event dataframe.
    df_events = df_events_arg.copy()
    tsu.returnize0(df_rets.values)

    if b_market_neutral == True:
        #bug! df_rets = df_rets - df_rets[s_market_sym]
        df_rets = df_rets.sub(df_rets[s_market_sym].values, axis=0)
        print "Passa", df_rets
        del df_rets[s_market_sym]
        del df_events[s_market_sym]

    df_close = df_close.reindex(columns=df_events.columns)

    # Removing the starting and the end events
    df_events.values[0:i_lookback, :] = np.NaN
    df_events.values[-i_lookforward:, :] = np.NaN

    # Number of events
    i_no_events = int(np.logical_not(np.isnan(df_events.values)).sum())
    assert i_no_events > 0, "Zero events in the event matrix"
    na_event_rets = "False"

    # Looking for the events and pushing them to a matrix
    for i, s_sym in enumerate(df_events.columns):
        for j, dt_date in enumerate(df_events.index):
            if df_events[s_sym][dt_date] == 1:
                na_ret = df_rets[s_sym][j - i_lookback:j + 1 + i_lookforward]
                if type(na_event_rets) == type(""):
                    na_event_rets = na_ret
                else:
                    na_event_rets = np.vstack((na_event_rets, na_ret))

    if len(na_event_rets.shape) == 1:
        na_event_rets = np.expand_dims(na_event_rets, axis=0)

    # Computing daily rets and retuns
    na_event_rets = np.cumprod(na_event_rets + 1, axis=1)
    na_event_rets = (na_event_rets.T / na_event_rets[:, i_lookback]).T

    # Study Params
    na_mean = np.mean(na_event_rets, axis=0)
    na_std = np.std(na_event_rets, axis=0)
    li_time = range(-i_lookback, i_lookforward + 1)

    # Plotting the chart
    plt.clf()
    plt.axhline(y=1.0, xmin=-i_lookback, xmax=i_lookforward, color='k')
    if b_errorbars == True:
        plt.errorbar(li_time[i_lookback:], na_mean[i_lookback:],
                    yerr=na_std[i_lookback:], ecolor='#110e4c',
                    alpha=0.1)
    plt.plot(li_time, na_mean, linewidth=3, label='mean', color='b')
    plt.xlim(-i_lookback - 1, i_lookforward + 1)
    if b_market_neutral == True:
        plt.title('Market Relative mean return of ' +\
                str(i_no_events) + ' events')
    else:
        plt.title('Mean return of ' + str(i_no_events) + ' events')
    plt.xlabel('Days')
    plt.ylabel('Cumulative Returns')
    plt.savefig(s_filename, format='pdf')
