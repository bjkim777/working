import os
import sys
import argparse

POS={}
COUNT={}

def GetOpts():
	parser = argparse.ArgumentParser(description = '')
	#parser.add_argument('-a', '--arg1', type=str, default='.', metavar='<arg1>',  help= 'description')
	parser.add_argument('-l', '--list', type=str, required=True,  metavar= '<adi file list>', help= 'adi file list')
	argv = parser.parse_args()
	return(argv)

	
def MkVAFDB(adi_file):
	with open(adi_file, 'r') as f:
		for line in f:
			if int(line.split('|')[1].strip()) == 2 :
				pos=line.strip().split()[1]
				ref_dp=float(line.strip().split()[2])
				alt_dp=float(line.strip().split()[3])
			else:
				continue
			
			vaf = alt_dp / (ref_dp + alt_dp)
			if str(pos)  in POS:
				POS[str(pos)]+=vaf
				COUNT[str(pos)]+=int(1)
			else:
				POS[str(pos)]=vaf
				COUNT[str(pos)]=int(1)

### MAIN ###
def main (file_list):
	index=[]
	with open(file_list, 'r') as f:
		for line in f:
			index.append(line.strip())

	for file in index:
		MkVAFDB(file)

	keys=COUNT.keys()
	keys.sort()

	for key in keys:
		print key, POS[str(key)]/COUNT[str(key)]

### ACTION ### 
if __name__ == "__main__":
	argv = GetOpts()

	main( argv.list)
	sys.exit(0)