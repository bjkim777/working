#FORMAT : vaf(%) count(average)
"""
example)
5 8
10 10
15 11
20 54
25 38
30 26
35 26
40 32
45 34
50 44
55 31
60 28
65 14
70 10
75 7
80 5
85 4
90 4
95 7
100 136
"""
import os
import sys
import argparse

COUNT={5:0, 10:0, 15:0, 20:0, 25:0, 30:0, 35:0, 40:0, 45:0, 50:0, 55:0, 60:0, 65:0, 70:0, 75:0, 80:0, 85:0, 90:0, 95:0}
#COUNT={5:0, 10:0, 15:0, 20:0, 25:0, 30:0, 35:0, 40:0, 45:0, 50:0, 55:0, 60:0, 65:0, 70:0, 75:0, 80:0, 85:0, 90:0, 95:0,100:0}

def GetOpts():
	parser = argparse.ArgumentParser(description = '')
	#parser.add_argument('-a', '--arg1', type=str, default='.', metavar='<arg1>',  help= 'description')
	parser.add_argument('-l', '--list', type=str, required=True,  metavar= '<adi file list>', help= 'adi file list')
	argv = parser.parse_args()
	return(argv)

	
	
def VAF(adi_file):
	with open(adi_file, 'r') as f:
		for line in f:
			if int(line.split('|')[1].strip()) == 2 or int(line.split('|')[1].strip()) == 3:
				ref_dp=float(line.strip().split()[2])
				alt_dp=float(line.strip().split()[3])
			else:
				continue
			vaf = alt_dp / (ref_dp + alt_dp)

			if vaf >= 0 and vaf <=0.05:
				COUNT[5]+=int(1)
			elif vaf > 0.05 and vaf <=0.10:
				COUNT[10]+=int(1)
			elif vaf > 0.10 and vaf <=0.15:
				COUNT[15]+=int(1)
			elif vaf > 0.15 and vaf <=0.20:
				COUNT[20]+=int(1)
			elif vaf > 0.20 and vaf <=0.25:
				COUNT[25]+=int(1)
			elif vaf > 0.25 and vaf <=0.30:
				COUNT[30]+=int(1)
			elif vaf > 0.30 and vaf <=0.35:
				COUNT[35]+=int(1)
			elif vaf > 0.35 and vaf <=0.40:
				COUNT[40]+=int(1)
			elif vaf > 0.40 and vaf <=0.45:
				COUNT[45]+=int(1)
			elif vaf > 0.45 and vaf <=0.50:
				COUNT[50]+=int(1)
			elif vaf > 0.50 and vaf <=0.55:
				COUNT[55]+=int(1)
			elif vaf > 0.55 and vaf <=0.60:
				COUNT[60]+=int(1)
			elif vaf > 0.60 and vaf <=0.65:
				COUNT[65]+=int(1)
			elif vaf > 0.65 and vaf <=0.70:
				COUNT[70]+=int(1)
			elif vaf > 0.70 and vaf <=0.75:
				COUNT[75]+=int(1)
			elif vaf > 0.75 and vaf <=0.80:
				COUNT[80]+=int(1)
			elif vaf > 0.80 and vaf <=0.85:
				COUNT[85]+=int(1)
			elif vaf > 0.85 and vaf <=0.90:
				COUNT[90]+=int(1)
			elif vaf > 0.90 and vaf <=0.95:
				COUNT[95]+=int(1)
			"""
			elif vaf > 0.95 and vaf <=1.00:
				COUNT[100]+=int(1)
			"""

### MAIN ###
def main (file_list):
	index=[]
	with open(file_list, 'r') as f:
		for line in f:
			index.append(line.strip())

	for file in index:
		VAF(file)

	keys=COUNT.keys()
	keys.sort()

	for key in keys:
		print key, COUNT[int(key)]/len(index)

### ACTION ### 
if __name__ == "__main__":
	argv = GetOpts()

	main( argv.list)
	sys.exit(0)