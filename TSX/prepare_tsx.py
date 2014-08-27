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

def locate_files(folder):
	'''copy xml file from tar directory to date folder (needed to create slc)'''
	path = os.path.join(folder, 'TSX-1.SAR.L1B')
	subfolder = os.listdir(path)[0]
	files = os.listdir(os.path.join(path,subfolder))
	for f in files:
		if f.endswith('xml'):
			xml = f
	xmlpath = os.path.join(path,subfolder,xml)
	kmlpath = os.path.join(path,subfolder,'SUPPORT','GEARTH_POLY.kml')

	return os.path.abspath(xmlpath), os.path.abspath(kmlpath)


def untar(file):
	'''Untar file from DLR'''
	directory = file.rstrip('tar.gz')
	if os.path.isdir(directory):
		print 'Directory exists... skipping untar step'
	else:
		print 'Untarring {0}...'.format(file)
		f = tarfile.open(file)
		f.extractall('.')
	
	return directory


def create_slc(directory):
	''' call make_slc_tsx.csh from date folder'''
	xmlpath, kmlpath = locate_files(directory)
	xml = os.path.basename(xmlpath)
	fulldate =  xml.split('_')[-1].split('T')[0]
	date = fulldate[2:]

	print '\nCreating SLC:\n', date, xml
	if not os.path.isdir(date):
		os.mkdir(date)
	os.chdir(date)

	# Create copies of footprint kml and xml metadata in date folder
	shutil.copyfile(xmlpath, date + '.xml')
	shutil.copyfile(kmlpath, date + '.kml')	

	# Call Walter Z's preprocessor
	cmd = 'make_slc_tsx -i {0} -p {1}'.format(xmlpath,date)
	print cmd
	if os.path.isfile(date + '.slc'):
		print '{0}.slc already exists, skipping creation...'.format(date)
	else:
		with open('make_slc_tsx.out','w') as out:
			subprocess.call(shlex.split(cmd), stdout=out)

	# in preparation for ROI_PAC, create empty raw files
	open('{0}.raw'.format(date),'w').close()
	shutil.copyfile('{0}.slc.rsc'.format(date), '{0}.raw.rsc'.format(date))

	# Run get_height.pl
	cmd = 'get_height.pl {0}'.format(date)
	print cmd
	subprocess.call(shlex.split(cmd))

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
