import os
import sys
import subprocess
import tempfile
import argparse

DB={}

def GetOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-d', '--db', type=str, required=True, metavar='<db>',  help= 'Population VAF DB')
	parser.add_argument('-f', '--file', type=str, required=True,  metavar= '<adi file>', help= 'adi file')
	argv = parser.parse_args()
	return(argv)

def MkDB(db):
	with open(db, 'r') as f:
		for line in f:
			pos = line.strip().split()[0]
			maf = line.strip().split()[1]

			DB[str(pos)]=float(maf)

def MatchPos(adi_file):
	with open(adi_file, 'r') as f:
		for line in f:
			if int(line.split('|')[1].strip()) == 2:
				pos=line.strip().split()[1]
				ref_dp=float(line.strip().split()[2])
				alt_dp=float(line.strip().split()[3])
			else:
				continue

			vaf = alt_dp/(ref_dp+alt_dp)

			if str(pos) in DB:
				print pos + ' ' + str(DB[str(pos)]) + ' ' + str(vaf)
			else:
				continue

### MAIN ###
def main (db, adi_file):
	MkDB(db)
	MatchPos(adi_file)

### ACTION ### 
if __name__ == "__main__":
	argv = GetOpts()

	main( argv.db, argv.file )
	sys.exit(0)