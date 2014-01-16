#!/usr/bin/env python
"""
Generate raw format for a bunch of zipped frame data downloaded from ASF

Author: Scott Henderson
"""

import os
import subprocess
import shlex
#import numpy as np
import shutil
import glob

# Start by unzipping all files in the directory
def unzip():
	#zipfiles = os.listdir('.')
	zipfiles = glob.glob('*.zip')
	print 'Unzipping all data...\n'
	for z in zipfiles:
		os.system('unzip {0}'.format(z))


def make_date_folders():
	print '\nMaking date folders...\n'
	zipfiles = glob.glob('*.zip')
	#could speed things up by only reading from some of files
	#sceneids = np.unique([ x[6:11] for x in zipfiles])
	#frames = np.unique([ x[11:15] for x in zipfiles])
	folders = [ x[:-4] for x in zipfiles]
	dates = []
	for f in folders:
		with open(f + '/workreport','r') as wr:
			lines = wr.readlines()
		
		# check for HV file - move to make_raw_alos step
		#nfiles =  [x for x in lines if x.startswith('Pdi_Cnt')]
		#if '5' in nfiles[0].split('=')[1]:
		#	HV = True
		
		# get date
		time = [x for x in lines if x.startswith('Img_SceneCenter')]
		date = time[0].split('"')[1][2:8]

		# make date folder if it doesn't exist
		if not os.path.isdir(date):
			os.mkdir(date)
			dates.append(date)

		# move important files to date folder
		os.system('mv {0}/IMG* {0}/LED* {1}'.format(f,date))
	
	#write list of dates to files
	with open('dates.txt','w') as f:
		dates.sort()
		f.write('\n'.join(dates))


def make_raw():
	print '\nRunning make_raw_alos.pl...\n'
	with open('dates.txt','r') as f:
		dates = f.readlines()
	dates = [x.strip() for x in dates] #strip newline characters
	
	for date in dates:
		print date
		os.chdir(date)
    	# Check for HV
		if len([x for x in os.listdir('.') if x.startswith('IMG-HV')]) > 0:
			fbd2fbs = 'FBD2FBS'
			# make a directory to store extra HV files
			print 'moving IMG-HV files to HVfiles directory'
			os.mkdir('HVfiles')
			os.system('mv *HV* HVfiles')
		else:
			fbd2fbs = 'NO'

		#NOTE: this command starts all at one. Might be better to do them in serial?
		cmd = 'make_raw_alos.pl IMG {0} {1} &> make_raw_alos.out'.format(date, fbd2fbs)
		print cmd
		#os.system(cmd)
		
		#Or.. (hopefully waits until finished!)
		with open('make_raw_alos.out','w') as out:
			subprocess.call(shlex.split(cmd), stdout=out)
		
		os.chdir('../')
		
	#return 'done' #NOTE: having the function return something prevents jobs from running in background. Doesn't appear to be true...


def clean_up():
	print '\n Removing tmp files and stashing raw_data...\n'
	os.mkdir('raw_data')
	os.system('mv ALPS* raw_data')
    
	with open('dates.txt','r') as f:
		dates = f.readlines()
		dates = [x.strip() for x in dates] #strip newline characters

	for date in dates:
		print date
		os.chdir(date)
		
		os.system('rm {0}-* IMG*PRM IMG*raw'.format(date))
		os.mkdir('raw_data')
		os.system('mv IMG* LED* raw_data')

		os.chdir('../')


if __name__ == '__main__':
	# NOTE: comment out commands below if you want to re-run make_raw w/o unzipping
	unzip()
	make_date_folders()
	make_raw()
	clean_up()
	print 'Done'
