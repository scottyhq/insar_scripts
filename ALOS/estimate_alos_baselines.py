#!/usr/bin/env python
"""
Estimate ALOS baselines from JAXA search csv file output

Based on a Matlab code by Yo Fukushima

Author: Scott Henderson
"""
import sys
import numpy as np
import pyproj

import matplotlib.pyplot as plt
import datetime 
from matplotlib.dates import MonthLocator, DateFormatter
import matplotlib.mlab as mlab


def make_baseline_plot(recarray,title):
    ''' More informative version using record array for a particular track'''
    fig = plt.figure(figsize=(11,8.5))
    ax = fig.add_subplot(111)
    
    # sort by beam mode
    fbs = (recarray.mode == 'FBS')
    fbd = -fbs
    
    #pltdates = np.array([datetime.datetime.strptime(date,'%Y/%m/%d') for date in recarray.date])
    #mlab.rec_append_fields(recarray,'pltdate',pltdates,object) # append datetime objects as new field
    
    plt.plot(recarray[fbs].pltdate, recarray[fbs].bperp, 'bo', label='FBS')
    plt.plot(recarray[fbd].pltdate, recarray[fbd].bperp, 'rs', label='FBD')
    
    #plot text shorthand date next to point
    for D,B in zip(recarray.pltdate,recarray.bperp):
        plt.text(D,B,D.strftime('%y%m%d'))
    
    plt.title(title)
    plt.ylabel('Perpendicular Baseline [m]')
    
    months   = MonthLocator()  # every month
    ax.xaxis.set_minor_locator(months)
    ax.fmt_xdata = DateFormatter('%Y-%m-%d') #lower left coodinate display
    fig.autofmt_xdate()
    
    plt.legend(loc='best', numpoints=1)
    plt.grid(True)
    plt.show()
    plt.savefig('baseline.ps')



def add_timespan(recarray):
    ''' input: array of dates as strings
        output: datetime list, dt relative to first date [days]'''
    pltdates = np.array([datetime.datetime.strptime(date,'%Y/%m/%d') for date in recarray.date])
    
    dt = np.cumsum(np.diff(pltdates)) #could do array of total seconds or decimal years
    dt = np.insert(dt,0,datetime.timedelta(0))
    
    roidates = np.array([D.strftime('%y%m%d') for D in pltdates])

    recarray = mlab.rec_append_fields(recarray,'dt',dt,object)
    recarray = mlab.rec_append_fields(recarray,'pltdate',pltdates,object) # append datetime objects as new field
    recarray = mlab.rec_append_fields(recarray,'roidate',roidates, roidates.dtype)
    #print "appended 'dt' and 'pltdate' fields"
    return recarray


def ecef2enu(pos, ref):
    """
    http://en.wikipedia.org/wiki/Geodetic_datum#Geodetic_versus_geocentric_latitude
    """
    xm,ym,zm = ref.flat #extracts elements of column or row vector
    # duplicate reference vector rows into matrix
    ref = np.vstack((ref,)*pos.shape[0])
       
    # get geodetic lat/lon/height (above wgs84) of satellite
    ecef = pyproj.Proj(proj='geocent',  ellps='WGS84', datum='WGS84')
    wgs84 = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    lon, lat, h = pyproj.transform(ecef, wgs84, xm, ym, zm, radians=True)

    # make transformation matrix
    transform = np.array([
        [-np.sin(lon), np.cos(lon), 0.0],
        [-np.sin(lat)*np.cos(lon), -np.sin(lat)*np.sin(lon), np.cos(lat)],
        [np.cos(lat)*np.cos(lon), np.cos(lat)*np.sin(lon), np.sin(lat)]
    ])
    
    # do matrix multiplication
    enu = np.dot(transform, pos.T - ref.T)
    
    return enu



def add_bperp(recarray):
    ''' input: position vector [m], velocity vector [m], offnadir angle [deg]
        output: perpendicular baseline [m] '''
    pos = np.vstack((recarray.x, recarray.y, recarray.z)).T * 1000
    vel = np.vstack((recarray.dx, recarray.dy, recarray.dz)).T * 1000
    
    x,y,z = np.hsplit(pos,3) #if pos.shape = (7,3)
    #dx,dy,dz = np.hsplit(vel,3)
    #x,y,z = pos[0],pos[1],pos[2] #pos is (3,7)
    offnadir = np.radians(recarray.offnadir)
    
    # Get mean parameters of satellite ((1,n) row vector)
    pos0 = np.mean(pos,0).reshape(1,-1) #average position of all acquisitions
    xm,ym,zm = pos0.flat
    vel0 = np.mean(vel,0).reshape(1,-1)
    
    # get geodetic lat/lon/height (above wgs84) of satellite
    ecef = pyproj.Proj(proj='geocent',  ellps='WGS84', datum='WGS84')
    wgs84 = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    lon, lat, h = pyproj.transform(ecef, wgs84, x, y, z, radians=True)
    h_ave = np.mean(h)
    
    # Convert geocentric coordinates to average ENU in plane of satellite
    xl,yl,zl = ecef2enu(pos, pos0)
    
    # Calculate travel direction in ENU coordinates from differencing unit velocity motion  
    # NOTE: not sure why this works..., need to *1000 to keep consistent w/ matlab code, but units don't exactly match
    pos1 = pos0 + vel0/np.linalg.norm(vel0)*1000
    pos2 = pos0 - vel0/np.linalg.norm(vel0)*1000
    p1,p2,p3 = ecef2enu(pos1, pos0)
    q1,q2,q3 = ecef2enu(pos2, pos0)
    vxl = q1 - p1
    vyl = q2 - p2
    vzl = q3 - p3
    
    # Along-track direction
    trackdir = np.arctan(vxl/vyl)
    
    # Calculate perpendicular baseline
    Bx = xl-xl[0]
    By = yl-yl[0]
    zr = h.flat-h_ave
    Br = zr-zr[0]
    #Bv = zl-zl[0]
    Bh = Bx*np.cos(trackdir) - By*np.sin(trackdir)
    
    Bperp = Bh*np.cos(offnadir) + Br*np.sin(offnadir)
    Bpara = Bh*np.sin(offnadir) - Br*np.cos(offnadir)
    
	# Match ROI_PAC Baseline sign convention for ascending data
    if trackdir < 0:
		Bperp = -Bperp

    recarray = mlab.rec_append_fields(recarray,'bperp',Bperp,float)
    #print "appended 'bperp' field"
    return recarray


def write_baseline_file(recarray, track):
    ''' write a simple ascii file with date and baseline columns '''
    subset = mlab.rec_keep_fields(recarray, ['roidate','bperp'])
    mlab.rec2csv(subset,'baselines.txt'.format(track), withheader=False, delimiter=' ')
	#NOTE: this is like dolist.in for batch processing 

def main(csvfile):
    ''' call other functions to produce baseline plots '''
    # see also csv2rec() & rec2csv
    #os.chdir('/home/scott/data/insar/alos')
    alldata = np.genfromtxt(csvfile,
                     skip_header=1,
                     delimiter=',',
                     comments='#',
                     usecols=(2,3,4,5,9,24,25,26,27,28,29),
                     names=('mode','date','track','frame','offnadir','x','y','z','dx','dy','dz'),
                     dtype=('|S4','|S10','i4','i4') + ('f4',)*7,
                    )
    
    for track in np.unique(alldata['track']):
        ind = (alldata['track'] == track) 
        data = alldata[ind]
        
		# If multiple frames in csv file, just plot first frame... could instead loop over them
        first_frame = data['frame'][0]
        ind = (data['frame'] == first_frame)
        data = data[ind]
        recarray = np.array(data.copy()).view(np.recarray) #allows attribute access recarray.date
        recarray = add_bperp(recarray)
        recarray = add_timespan(recarray)

        title = 'path={0}, frame={1}'.format(track, first_frame)
        make_baseline_plot(recarray, title)
        write_baseline_file(recarray, track)
    

if __name__ == '__main__':
	csvfile = sys.argv[1]
	main(csvfile)
