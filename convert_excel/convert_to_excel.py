from __future__ import print_function	# print stderr
import os
import sys
import argparse
from pandas import Series, DataFrame
import pandas as pd
import openpyxl # check : pip install openpyxl

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-a', '--ann', type=str,  required=True, metavar='<annotation file>',  help= 'tab delimeter file')
	argv = parser.parse_args()
	return(argv)

def convertExcel(ann):
	# -------------------------------
	# Make index
	# -------------------------------
	HEAD=[]
	BOX=[]

	# -------------------------------
	# Make Data
	# -------------------------------
	with open(ann) as f:
		for index, line in enumerate(f):
			col=line.strip().split('\t')

			if index==0:
				HEAD=col
			else:
				BOX.append(col)
			
	# -------------------------------
	# Make DataFrame
	# -------------------------------	
	MATRIX=DataFrame(BOX, columns=HEAD).sort_index()

	# -------------------------------
	# Make stat file to Excel
	# -------------------------------
	writer=pd.ExcelWriter(ann+'.xlsx') # pip install openpyxl
	MATRIX.to_excel(writer, 'annotation')
	writer.save()

### MAIN ###
def main (ann):
	convertExcel(ann)
			

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main(argv.ann)
	sys.exit(0)