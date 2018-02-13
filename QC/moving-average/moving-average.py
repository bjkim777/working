import os
import sys
import argparse

COUNT_DEPTH={}

def GetOpts():
	parser = argparse.ArgumentParser(description = '')
	#parser.add_argument('-a', '--arg1', type=str, default='.', metavar='<arg1>',  help= 'description')
	parser.add_argument('-f', '--file',  required=True,  metavar= '<file>', help= 'samtools depth file')
	argv = parser.parse_args()
	return(argv)

def CountDepth(depth):
	if int(depth) in COUNT_DEPTH:
		COUNT_DEPTH[int(depth)]+=int(1)
	else:
		COUNT_DEPTH[int(depth)]=int(1)


def MkList(index, length, degree=10):
	if degree%2==0:
		forward=degree/2
		behind=degree/2
	else:
		forward=(degree-1)/2
		behind=(degree-1)/2+1

	if str(index-forward).isdigit():
		start=index-forward
	else:
		start=0

	if index+behind > length-1:
		end= length
	else:
		end = index+behind
	return (range(start,end))

### MAIN ###
def main (depth_file):

	with open(depth_file, 'r') as f:
		for line in f:
			depth=line.strip().split()[2]
			CountDepth(depth)

	keys=COUNT_DEPTH.keys()
	keys.sort()
	
	for index, key in enumerate(keys):
		sum_target = 0
		target_list = MkList(index, len(keys))
		for target in target_list: 
			sum_target+=COUNT_DEPTH[int(keys[target])]

		print key, sum_target/len(target_list)


			

### ACTION ### 
if __name__ == "__main__":
	argv = GetOpts()

	main( argv.file )
	sys.exit(0)
