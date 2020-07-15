import sys
import argparse
import re
import subprocess

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-d', '--data', type=str, required=True,  metavar= '<data path>', help= 'data path')
	argv = parser.parse_args()
	return(argv)

def changeData(data):
	with open(data, 'r') as f:
		PATTEN = ""
		for line in f:
			if re.match("-",line):
				size = line.strip().split()[4]
				#date = subprocess.Popen(['date','-d'," ".join(line.strip().split()[5:8]),'+%s'], stdout=subprocess.PIPE).stdout.readlines()[0].strip()
				data = line.strip().split()[-1]

				if PATTEN:
					print ("{path}/{file}|{size}".format(path=PATTEN, file=data, size=size))
				else:
					print ("{file}|{size}".format(file=data, size=size))

			elif len(line.strip().split())==1 and re.search(":$", line):
				PATTEN = line.strip().split(':')[0]

### MAIN ###
def main (data):
	changeData(data)
			

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main( argv.data )
	sys.exit(0)
