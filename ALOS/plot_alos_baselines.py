#!/usr/bin/env python
"""
Baseline plot for directory of ALOS data, with dates colored by PRF

Author: Scott Henderson
"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import datetime 
from matplotlib.dates import MonthLocator, DateFormatter
import matplotlib.mlab as mlab

def load_rsc(path):
    """
    Read metadata from .rsc file into python dictionary
    """
    metadata = {}
    rsc = open(path + '.rsc', 'r')
    # Remove blank lines, retaining only lines with key, value pairs
    allLines = [line for line in rsc.readlines() if line.strip()]
    for line in allLines:
		items = line.split()
		var = items[0]
		value = '_'.join(items[1:]) #replace space w/underscore
		metadata[var] = value
    rsc.close()
    return metadata


def get_PRF(dates):
	prfs = np.zeros(dates.size)
	for i,date in enumerate(dates):
		rsc = load_rsc('{0}/{0}.raw'.format(date))
		prfs[i] = float(rsc['PRF'])

	#print prfs
	return prfs	


def make_baseline_plot(baseline_file):
    ''' More informative version using record array for a particular track'''
    fig = plt.figure(figsize=(11,8.5))
    ax = fig.add_subplot(111)
    
	# Load date and baseline data from file
    #dates, bperps = np.loadtxt(baseline_file,unpack=True)
    dates, bperps = np.genfromtxt(baseline_file,unpack=True,comments='#',dtype=str) #easiest way to get columns of text, then convert after
    bperps = bperps.astype('f4')
	#print dates

    pltdates = np.array([datetime.datetime.strptime(date,'%y%m%d') for date in dates])
    #dt = np.cumsum(np.diff(pltdates)) #could do array of total seconds or decimal years 
    #dt = np.insert(dt,0,datetime.timedelta(0))
    #print pltdates
    prfs = get_PRF(dates)

    #plt.plot(pltdates,bperps,'ro',label='estimation')
	#NOTE: pltdates not woriking with scatter plot for some reason?!
    #print pltdates,bperps,prfs
    unique_prfs = np.unique(prfs)
    cmap = plt.get_cmap('jet', unique_prfs.size) #discrete colors!
    sc = plt.scatter(pltdates,bperps,s=80,c=prfs,cmap=cmap)
    cb = plt.colorbar(sc,ticks=unique_prfs,format='%.2f')
    cb.set_label('PRF [Hz]') #automatically sets long axis label
    #cb.ax.set_xlabel('PRF [Hz]',labelpad=30) #label on top of colorbar?

    #plot text shorthand date next to point
    for D,B in zip(pltdates, bperps):
        plt.text(D,B,D.strftime('%y%m%d'))    

    # add baselines estimated by python script
    #estimate_file = 'baselines.txt'
    #estimate_file = 'baselines_bottom.txt'
    #dates, bperps = np.genfromtxt(estimate_file,unpack=True,comments='#',dtype=str)
    #pltdates = np.array([datetime.datetime.strptime(date,'%y%m%d') for date in dates])
    #plt.plot(pltdates,bperps,'ko',label='estimate')

    plt.title(os.getcwd())
    plt.ylabel('B_Perp [m]')
    
    months   = MonthLocator()  # every month
    ax.xaxis.set_minor_locator(months)
    ax.fmt_xdata = DateFormatter('%Y-%m-%d') #lower left coodinate display
    fig.autofmt_xdate()
    
    plt.legend(loc='upper left', numpoints=1) #note: legend='best' doesn;t always work
    plt.grid(True)
    plt.savefig('baseline.ps')
    plt.show()


if __name__ == '__main__':
	basefile = sys.argv[1]
	make_baseline_plot(basefile)
