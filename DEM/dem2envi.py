#!/usr/bin/env python
"""
Quickly convert dem to envi format for using gdal tools

Usage: dem2envi.py file

"""
import sys

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
    
def write_envi_header(path,rsc):
    """
    write envi header format to use ROI_PAC dem with gdal
    """
    # need to strip negative in rsc 
    rsc['Y_STEP'] = rsc['Y_STEP'].strip('-')
    
    with open(path + '.hdr', "w") as f: #NOTE: automatically closes file
        f.write("""ENVI
description =   {0}
samples =       {WIDTH}
lines =         {FILE_LENGTH}
bands =         1
file type =     ENVI Standard
data type =     2
interleave =    bsq
byte order =    0
map info =      {{Geographic Lat/Lon, 1.0000, 1.0000, {X_FIRST}, {Y_FIRST}, {X_STEP}, {Y_STEP}, WGS-84, units=Degrees}}
""".format(path,**rsc))



if __name__ == '__main__':
    path = sys.argv[1]
    rsc = load_rsc(path)
    write_envi_header(path,rsc)
    print 'Done. to convert to geotif run:\ngdal_translate {0}.dem {0}.tif'.format(path[:-4])
    
    
