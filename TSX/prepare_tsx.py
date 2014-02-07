#!/usr/bin/env python
"""
unarchive tsx data from DLR into ROI_PAC directory structure to start from 'slcs'

Usage: prepare_tsx.py 
"""

import shutil
import sys 
import os
from optparse import OptionParser
import tarfile
import subprocess
import shlex

# Note: for specific computer... ensure correct library paths
# os.environ['LD_LIBRARY_PATH'] = "/usr/lib:/usr/lib64:/usr/local/lib:/usr/local/netcdf-3.6.3/lib"

def read_xml(folder):
	'''copy xml file from tar directory to date folder (needed to create slc)'''
	path = os.path.join(folder, 'TSX-1.SAR.L1B')
	subfolder = os.listdir(path)[0]
	files = os.listdir(os.path.join(path,subfolder))
	for f in files:
		if f.endswith('xml'):
			xml = f
	fulldate =  xml.split('_')[-1].split('T')[0]
	date = fulldate[2:]
	xmlpath = os.path.join(path,subfolder,xml)

	return date, os.path.abspath(xmlpath)


def untar(file):
	'''Untar file from DLR'''
	directory = file.rstrip('tar.gz')
	if os.path.isdir(directory):
		print 'directory exists... skipping untar'
	else:
		print 'Untarring {0}...'.format(file)
		f = tarfile.open(file)
		f.extractall('.')
	
	return directory


def create_slc(directory):
	''' call make_slc_tsx.csh from date folder'''
	date, xmlpath = read_xml(directory)
	xmlname = os.path.basename(xmlpath)

	print '\nCreating SLC:\n', date, xmlname
	if not os.path.isdir(date):
		os.mkdir(date)

	if not os.path.isfile( os.path.join(date, xmlname) ):	
		os.symlink(xmlpath, os.path.join(date, xmlname)) #create symlink for future reference (expand in python with os.path.realpath
	
	os.chdir(date)

	cmd = 'make_slc_tsx.csh {0} {1}'.format(xmlpath,date)
	#print cmd
	if os.path.isfile(date + '.slc'):
		print '{0}.slc already exists, skipping creation...'.format(date)
	else:
		with open('make_slc_tsx.out','w') as out:
			subprocess.call(shlex.split(cmd), stdout=out)

	# in preparation for ROI_PAC, create raw files
	open('{0}.raw'.format(date),'w').close()
	shutil.copyfile('{0}.slc.rsc'.format(date), '{0}.raw.rsc'.format(date))
	
	return date + '.slc'


def done_message(slc):
	#NOTE: could check baseline first: (grep rsc file for P_BASELINE_TOP_HDR	
	print '\nCreated {0}.\nReady to run ROI_PAC from slcs:\n'.format(slc)
	cmd1 = 'process_2pass.pl [?].proc roi_prep orbbase'
	print cmd1
	cmd2 = 'process_2pass.pl [?].proc slcs done_sim_removal'
	print cmd2


def main():
	#args = ['-n'] #testing
	parser = OptionParser(usage="Usage %prog [options] dims_file", version="%prog 1.0") 
	(options, args) = parser.parse_args()
	if len(args) != 1:
		parser.error("must specify dims_ directory or tar file")
	if not os.path.exists(args[0]):
		parser.error("{0} not found".format(args[0]))

	file = args[0]
	if os.path.isdir(file):
		directory = file
	else:
		directory = untar(file)
	slc = create_slc( directory) 
	done_message(slc)


if __name__ == '__main__':
	main()
