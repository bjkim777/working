from __future__ import print_function	# print stderr
import os
import sys
import subprocess
import argparse
import math
from pandas import Series, DataFrame
import pandas as pd
import openpyxl # check : pip install openpyxl

SAMTOOLS='/usr/local/bin/samtools'

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-p', '--path', action='append', required=True, nargs='*', metavar= 'path', help= 'You can use multiple arguments. ex) path1 path2 path3')
	parser.add_argument('-e', '--ext', type=str,  required=True, metavar='<filename extension>',  help= 'filename extension. ex) adi, bam')
	argv = parser.parse_args()
	return(argv)

def checkResult(result_paths, ext):
	file_list=[]

	# make file list
	for result_path in result_paths:
		for (path, dir, files) in os.walk(result_path):
			for file in files:
				if ext in os.path.splitext(file)[-1]: # check filename extension
					file_list.append(os.path.join(path, file))

	if ext =='adi' or ext == 'bam':
		# -------------------------------
		# Make index
		# -------------------------------
		KEY=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
			'11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
			'21', '22', 'X', 'Y', 'M']
		SAMPLE=[]
		BOX=[]

		for file in file_list:
			SAMPLE.append(file.split('/')[-1])

			# -------------------------------
			# Adiscan result stat(count variants)
			# -------------------------------
			if ext == 'adi':
				# first method
				"""		
				line=subprocess.Popen(['tail', '-n1', file], stdout=subprocess.PIPE).stdout.readlines()[0]
				pos=line.split()[1]
				
				if len(pos.split('_'))>2:
					pass
				else:
					if 'M' in pos.split('_')[0] or 'X' in pos.split('_')[0] or 'Y' in pos.split('_')[0]:
						pass
					else:
						print ('{0}\t{1}'.format(pos, file))
				"""
				CHR={'1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0, '10':0,
					'11':0, '12':0, '13':0, '14':0, '15':0, '16':0, '17':0, '18':0, '19':0, '20':0,
					'21':0, '22':0, 'X':0, 'Y':0, 'M':0}
				RESULT=[]

				with open(file, 'r') as f:
					for line in f:
						pos=line.strip().split()[1]
						
						if len(pos.split('_')) > 2:
							continue
						else:
							if 'chr' in pos:
								
								if 'M' in pos:
									chr=pos.split('_')[0][3:4]
								else:
									chr=pos.split('_')[0][3:]
							else:
								if 'M' in pos:
									chr=pos.split('_')[0][0:1]
								else:
									chr=pos.split('_')[0][0:]

						if str(chr) in CHR:
							CHR[str(chr)]+=1
						else:
							CHR[str(chr)]=1

				for chr in KEY:
					RESULT.append(CHR[str(chr)])
				BOX.append(RESULT)
		
			# -------------------------------
			# BAM stat(count mapping reads)
			# -------------------------------
			elif ext == 'bam':
				def checkFiles(*tools):
					index=0
					for LIST in [x for x in tools]:
						if os.path.exists(LIST):
							pass
						else:
							print ('{file} is not exist.'.format(file=LIST), file=sys.stderr)
							index+=1
				
					if not index==0:
						raise Exception('Files are not exist.')

				checkFiles(SAMTOOLS)

				CHR={}
				RESULT=[]

				stats=subprocess.Popen([SAMTOOLS, 'idxstats', file], stdout=subprocess.PIPE)

				for stat in stats.stdout.readlines():
					pos=stat.split()[0]
					ALIGN=stat.split()[2]

					if 'chr' in pos:
						if 'M' in pos:
							chr=pos[3:4]
						else:
							chr=pos[3:]
					else:
						if 'M' in pos:
							chr=pos[0:1]
						else:
							chr=pos[0:]

					CHR[str(chr)]=ALIGN

				for chr in KEY:
					RESULT.append(CHR[str(chr)])
				BOX.append(RESULT)

		# -------------------------------
		# Make DataFrame
		# -------------------------------	
		MATRIX=DataFrame(BOX, columns=KEY, index=SAMPLE).sort_index()

		# -------------------------------
		# Find 0 line
		# -------------------------------
		print('####### Find empty chromosome #######')
		print('#File\tEmpty-Chr\tTotal-count')
		for sample in SAMPLE:
			for key in KEY:
				if MATRIX.loc[sample,key] == 0:
					print('{0}\t{1}\t{2}'.format(sample, key, MATRIX.loc[sample].sum()))
					break
				else:
					continue

		# -------------------------------
		# Statistics
		# -------------------------------
		print('####### Statistics #######')
		print(MATRIX.sum(axis=1).describe())

		# -------------------------------
		# Make stat file to Excel
		# -------------------------------
		writer=pd.ExcelWriter('stat.xlsx') # pip install openpyxl
		if ext=='bam':
			MATRIX.to_excel(writer, 'count mapping reads')
		elif ext=='adi':
			MATRIX.to_excel(writer, 'count variants')
		writer.save()

	# -------------------------------
	# IQR
	# -------------------------------
	size_list=[]
	for i, file in enumerate(file_list):
		size=os.path.getsize(file)
		size_list.append([int(size), int(i)])

	def findOutlier(list):
		list.sort()
		q1_index, q3_index =((len(list)+1)/4)-1 , ((len(list)+1)*3/4)-1  # why -1 : list index

		if q1_index < 0:
			q1_index=0
			print ('{0} sample : too few to try IQR.'.format(len(list)))

		if len(list)%2 is 0:
			q1=(list[int(q1_index)][0]+list[int(math.ceil(q1_index))][0])/2
			q3=(list[int(q3_index)][0]+list[int(math.ceil(q3_index))][0])/2
		else:
			q1, q3 = list[q1_index][0], list[q3_index][0]

		iqr=q3-q1

		return [x for x in list if x[0] < q1-iqr*1.5]

	print('####### Find outlier(data size) #######')
	print('#File\tSize(MB)')
	outlier_list=findOutlier(size_list)
	if outlier_list:
		for list in outlier_list:
			print ('{0}\t{1}'.format(file_list[list[1]], round(float(list[0])/(1024**2), 2)))
	else:
		#print('No outlier!')
		pass

	print ('Complete checking!')

### MAIN ###
def main (result_paths, ext):
	checkResult(result_paths[0], ext)
			

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main(argv.path, argv.ext )
	sys.exit(0)
