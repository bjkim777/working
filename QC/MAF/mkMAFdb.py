import os
import sys
import subprocess
import tempfile
import argparse

POS={}

def GetOpts():
	parser = argparse.ArgumentParser(description = '')
	#parser.add_argument('-a', '--arg1', type=str, default='.', metavar='<arg1>',  help= 'description')
	parser.add_argument('-l', '--list', type=str, required=True,  metavar= '<adi file list>', help= 'adi file list')
	argv = parser.parse_args()
	return(argv)

def CountPos(adi_file):
	with open(adi_file, 'r') as f:
		for line in f:	
			if int(line.split('|')[1].strip()) == 2 or int(line.split('|')[1].strip()) == 3:

				pos=line.strip().split()[1]
				if str(pos) in POS:
					POS[str(pos)]+=int(1)
				else:
					POS[str(pos)]=int(1)
			else:
				continue


### MAIN ###
def main (file_list):
	index=[]
	with open(file_list, 'r') as f:
		for line in f:
			index.append(line.strip())

	for file in index:
		CountPos(file)

	keys=POS.keys()
	keys.sort()

	for key in keys:
		print key, POS[str(key)]/float(len(index)),  POS[str(key)], len(index)
			

### ACTION ### 
if __name__ == "__main__":
	argv = GetOpts()

	main( argv.list)
	sys.exit(0)