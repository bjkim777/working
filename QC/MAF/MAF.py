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
	sample_dp_maf = tempfile.NamedTemporaryFile(delete=False,bufsize=1)

	with open(adi_file, 'r') as f:
		for line in f:
			pos = line.strip().split()[1]
			ref_dp = line.strip().split()[2]
			alt_dp = line.strip().split()[3]

			if str(pos) in DB:
				sample_dp_maf.write(str(int(ref_dp) + int(alt_dp)) + ' ' + str(DB[str(pos)]) + '\n' )
				#print str(int(ref_dp) + int(alt_dp)) + ' ' + str(DB[str(pos)])
			else:
				sample_dp_maf.write(str(int(ref_dp)+int(alt_dp)) + ' ' + str(0) + '\n')
				#print str(int(ref_dp)+int(alt_dp)) + ' ' + str(0)

	return (sample_dp_maf.name)
"""
def MkGraphInput(data):
	POS2MAF={}

	with 
"""
def file_len(fname):
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return float(i+1)


### MAIN ###
def main (db, adi_file):
	MkDB(db)
	sample_dp_maf=MatchPos(adi_file)
	maf10 = tempfile.NamedTemporaryFile(delete=False, bufsize=1)
	maf5 = tempfile.NamedTemporaryFile(delete=False, bufsize=1)
	maf0 = tempfile.NamedTemporaryFile(delete=False, bufsize=1)

	max=0
	with open(sample_dp_maf, 'r') as  f:
		for line in f:
			depth=int(line.strip().split()[0])
			maf=float(line.strip().split()[1])

			if max<depth:
				max=depth

			if maf > 0.1:
				maf10.write(line)
			elif maf >= 0.05 and maf <= 0.1:
				maf5.write(line)
			elif maf < 0.05:
				maf0.write(line)

	degree=range(100,int(max)+100, 100)
	TMP={}
	file_list=[maf0.name, maf5.name, maf10.name]

	for file in file_list:
		TMP[file]=tempfile.NamedTemporaryFile(delete=False, bufsize=1).name
		COUNT={}
		with open(file, 'r') as f:
			for line in f:
				depth=int(line.strip().split()[0])

				for index in range(len(degree)):
					if depth <= degree[index]:
						if degree[index] in COUNT:
							COUNT[degree[index]]+=int(1)
						else:
							COUNT[degree[index]]=int(1)
		
		for key in degree:
			with open(TMP[file], 'a') as f:
				f.write(str(COUNT[key]/file_len(file)) + '\n')

	head=tempfile.NamedTemporaryFile(delete=False, bufsize=1)
	for i in degree:
		head.write(str(i)+'\n')
	
	tmp=subprocess.Popen(['paste',head.name, TMP[maf0.name], TMP[maf5.name], TMP[maf10.name]], stdout=subprocess.PIPE)

	for line in tmp.stdout.readlines():
		print line.strip()

	subprocess.call(['rm', sample_dp_maf, head.name, maf0.name, maf5.name, maf10.name, TMP[maf0.name], TMP[maf5.name], TMP[maf10.name]])

### ACTION ### 
if __name__ == "__main__":
	argv = GetOpts()

	main( argv.db, argv.file )
	sys.exit(0)