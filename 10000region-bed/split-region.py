import os
import sys
import subprocess
import tempfile
import argparse

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-b', '--bed', type=str, required=True,  metavar= '<bed>', help= 'bed file')
	argv = parser.parse_args()
	return(argv)

def splitRegion(BED):
	MAX_REGION=10000
	NAME=BED.split(".bed")[0]

	OUTPUT=NAME+"-split.bed"

	if os.path.exists(OUTPUT):
		subprocess.call(['rm', '-f', OUTPUT])

	with open(BED, 'r') as f:
		for line in f.readlines():
			col=line.strip().split('\t')

			chr=col[0]
			start=col[1]
			end=col[2]
			ann=col[3:]

			with open(OUTPUT, 'a') as output:
				if int(end)-int(start)>=MAX_REGION:

					def Region(num):
						if num % MAX_REGION ==0:
							return range(1, int(num/MAX_REGION)+1)
						else:
							return range(1, int(num/MAX_REGION)+2)

					"""
					example)

					2	20022

						V

					2	10001 : length 10000
					10002	20001 : length 10000
					20002	20022 : length 21

					"""

					for i in Region(int(end)-int(start)):
						if i==len(Region(int(end)-int(start))):
							output.write('{chr}\t{start}\t{end}\t{ann}\n'.format(chr=chr, start=int(start)+MAX_REGION*i-MAX_REGION, end=int(end), ann='\t'.join(ann)).replace('\t\n', '\n'))
						else: 
							output.write('{chr}\t{start}\t{end}\t{ann}\n'.format(chr=chr, start=int(start)+MAX_REGION*i-MAX_REGION, end=int(start)+MAX_REGION*i-1, ann='\t'.join(ann)).replace('\t\n', '\n'))
						
				else:
					output.write('{chr}\t{start}\t{end}\t{ann}\n'.format(chr=chr, start=start, end=end, ann='\t'.join(ann)).replace('\t\n', '\n'))

	return output

### MAIN ###
def main (bed):
	splitRegion(bed)

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main(argv.bed)
	sys.exit(0)
