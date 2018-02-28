#!/usr/bin/python

from __future__ import print_function
import os
import sys
import subprocess
import argparse

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-l', '--list', type=str, metavar='<file list or directory list>',  help= 'backup list')
	parser.add_argument('-d', '--disk', action='append', required=True, nargs='*', metavar= 'disk', help= 'You can use multiple arguments. ex) /disk1 /disk2 /disk3')
	argv = parser.parse_args()
	return(argv)

def decideDisk(input, disk_list):

	DISK={}
	for index, o in enumerate(disk_list):
		DISK[int(index)]=str(o)

	def freeSpace(path):
		"""
		Returns the number of free bytes on the drive that path is on
		"""
		s=os.statvfs(path)
		return s.f_bsize * s.f_bavail

	def checkSpace(index, sum, file):
		MAX=0.85
		
		try:
			if freeSpace(DISK[index])*MAX < sum:
				sum=os.path.getsize(file)
				index+=1
				checkSpace(index, sum, file)
			else:
				if file[0] is '/':
					print('mkdir -p {output} ; cp {file} {output}'.format(file=file, output=DISK[index]+"/"+'/'.join(file.split('/')[2:-1])))
				else:
					print('mkdir -p {output} ; cp {file} {output}'.format(file=file, output=DISK[index]+"/"+'/'.join(file.split('/')[1:-1])))
		except KeyError:
			print('{} dose not allocate in disk.'.format(file), file=sys.stderr)

	sum=0
	index=0
	for what in input:
		if os.path.isdir(what.strip()): # check dir
			for (path, dir, files) in os.walk(what.strip()):
				for file in files:
					sum+=os.path.getsize(os.path.join(path, file))
					checkSpace(index, sum, os.path.join(path, file))

		else:
			sum+=os.path.getsize(what.strip())
			checkSpace(index, sum, what.strip())

### MAIN ###
def main (list, disk):
	file_list=[]

	with open(list, 'r') as f:
		for file in f:
			file_list.append(file.strip())

	decideDisk(file_list, disk[0])

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main(argv.list, argv.disk)
	sys.exit(0)
