#!/usr/bin/env python
"""
Baseline plot for directory of ALOS or TSX data, with dates colored by PRF

Usage: plot_baselines_prf.py [baseline_file]

baselines_prf.txt can be created with:
1) If ROI_PAC hasn't been run yet:
get_roi_baselines.py 111019

2) If it has (sometimes awk/mawk/gawk/ depending on platform):
grep PRF 1*/*raw.rsc | awk '{ print $2}' > prfs.txt
grep P_BASELINE_TOP int*111019/*baseline.rsc | awk '{{print substr($1,5,6)" "$2}}' > dolist.in
cat baselines.txt '111019 0\n' > baselines.txt
paste baselines.txt prfs.txt > baselines_prfs.txt

Author: Scott Henderson
"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import datetime 
from matplotlib.dates import MonthLocator, DateFormatter
import matplotlib.mlab as mlab


def make_baseline_plot(baseline_file):
    ''' More informative version using record array for a particular track'''
    fig = plt.figure(figsize=(11,8.5))
    ax = fig.add_subplot(111)
    
	# Load date and baseline data from file
    dates, bperps, prfs = np.genfromtxt(baseline_file,unpack=True,comments='#',dtype=str) #easiest way to get columns of text, then convert after
    prfs = prfs.astype('f4')
    bperps = bperps.astype('f4')
    unique_prfs = np.unique(prfs)

    pltdates = np.array([datetime.datetime.strptime(date,'%y%m%d') for date in dates])
    #colors = plt.cm.cool(unique_prfs/unique_prfs.max()) #color scaled by PRF value
    colors = plt.cm.cool(np.linspace(0,1,unique_prfs.size)) #max dicrete color separation
    for p,color in zip(unique_prfs,colors):
		ind = (prfs == p)
		plt.scatter(pltdates[ind], bperps[ind], s=100, c=color, label=p)

    #plot text shorthand date next to point
    for D,B in zip(pltdates, bperps):
        plt.text(D,B,D.strftime('%y%m%d'))    

    plt.title(os.getcwd())
    plt.ylabel('B_Perp [m]')
    
    months   = MonthLocator()  # every month
    ax.xaxis.set_minor_locator(months)
    ax.fmt_xdata = DateFormatter('%Y-%m-%d') #lower left coodinate display
    fig.autofmt_xdate()
    
    plt.legend(loc='upper left', title='PRF [Hz]', scatterpoints=1) #note: legend='best' doesn;t always work
    plt.grid(True)
    plt.savefig('baseline_plot.pdf',bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
	basefile = sys.argv[1]
	make_baseline_plot(basefile)
