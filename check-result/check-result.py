import os
import sys
import subprocess
import tempfile
import argparse
import math

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-p', '--path', action='append', required=True, nargs='*', metavar= 'path', help= 'You can use multiple arguments. ex) path1 path2 path3')
	parser.add_argument('-e', '--ext', type=str,  required=True, metavar='<filename extension>',  help= 'filename extension. ex) adi, bam')
	argv = parser.parse_args()
	return(argv)

def checkResult(result_paths, ext):
	file_list=[]
	size_list=[]

	# make file list
	for result_path in result_paths:
		for (path, dir, files) in os.walk(result_path):
			for file in files:
				if ext in os.path.splitext(file)[-1]: # check filename extension
					file_list.append(os.path.join(path, file))

	if ext is 'adi':
		for file in file_list:
			line=subprocess.Popen(['tail', '-n1', file], stdout=subprocess.PIPE).stdout.readlines()[0]
			pos=line.split()[1]
		
			if len(pos.split('_'))>2:
				pass
			else:
				if 'M' in pos.split('_')[0] or 'X' in pos.split('_')[0] or 'Y' in pos.split('_')[0]:
					pass
				else:
					print ('{0}\t{1}'.format(pos, file))

	else:
		# make size list
		for i, file in enumerate(file_list):
			size=os.path.getsize(file)
			size_list.append([int(size), int(i)])

		# -------------------------------
		# IQR
		# -------------------------------
		def findOutlier(list):
			list.sort()
			q1_index, q3_index =(len(list)+1)/4 , (len(list)+1)*3/4

			if len(list)%2 is 0:
				q1=(list[int(q1_index)][0]+list[int(math.ceil(q1_index))][0])/2
				q3=(list[int(q3_index)][0]+list[int(math.ceil(q3_index))][0])/2
			else:
				q1, q3 = list[q1_index][0], list[q3_index][0]

			iqr=q3-q1

			return [x for x in list if x[0] < q1-iqr*1.5]

		outlier_list=findOutlier(size_list)
		if outlier_list:
			for list in outlier_list:
				print ('{0}\t{1}'.format(round(float(list[0])/(1024**2), 2), file_list[list[1]]))
		else:
			print('No error!')



### MAIN ###
def main (result_paths, ext):
	checkResult(result_paths[0], ext)
			

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main(argv.path, argv.ext )
	sys.exit(0)
