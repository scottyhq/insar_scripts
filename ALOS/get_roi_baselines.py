#!/usr/bin/env python
'''
Call ROI_PAC process_2pass.pl from raw to orbbase for  combinations with master date

NOTE: calls process_2pass.pl *.proc roi_prep orbbase
which overwrites early processing files if it's already been done!

probably could write PRF to this file too!

Author: Scott Henderson
'''
import sys
import os
import glob
from numpy import genfromtxt

masterdate = sys.argv[1]

# Write .proc files with master date
dates = genfromtxt('dates.txt',dtype=str).tolist()
dates.remove(masterdate)
for d in dates:
	procname = 'int_{0}_{1}.proc'.format(d,masterdate) 
	with open(procname, 'w') as f:
		f.write('''SarDir1={0}
SarDir2={1}
IntDir=int_{0}_{1}
SimDir=int_{0}_{1}/SIM
GeoDir=int_{0}_{1}/GEO
flattening         = topo

BaselineOrder      = QUAD

DEM=/home/mpguest/final.dem
OrbitType=HDR
Rlooks_sim=4
Rlooks_geo=4
Rlooks_int=4
Rlooks_unw=16
pixel_ratio=2

concurrent_roi=yes
'''.format(d,masterdate))

# Run ROI_PAC to orbbase
inputs = glob.glob('*{}.proc'.format(masterdate))
for proc in inputs:
	cmd = 'process_2pass.pl {} raw orbbase'.format(proc)	
	print cmd	
	os.system(cmd)

# Extract baseline values from rscs and write to dolist.in file
cmd = "grep P_BASELINE_TOP int*{0}/*baseline.rsc | mawk '{{print substr($1,5,6)\" \"$2}}' > dolist.in".format(masterdate)
print cmd
os.system(cmd)

#add master date to dolist.in
with open('dolist.in','r') as f:
	lines = f.readlines()

lines.insert(0, '{} 0\n'.format(masterdate))

with open('dolist.in','w') as f:
	f.writelines(lines)

# Remove ROI_PAC output
cmd = 'rm -r int* log*'
print 'to remove files:\n',cmd
#os.system('rm -r int* log*')

print 'Wrote dolist.in file'
