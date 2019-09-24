import os
import sys
import argparse
import pandas as pd
import openpyxl

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-p', '--path', action='append', required=True, nargs='*', metavar='<path>',  help= 'Yon can use multiple arguments. ex) path1 path2 path3')
	parser.add_argument('-b', '--bed', type=str, required=True,  metavar= '<bed>', help= 'bed format : chr\tstart_pos\tend_pos')
	argv = parser.parse_args()
	return(argv)

def SERIES_selectGenotype(ADI):
	"""
	ADI format
	-----------------------
	chr chr1_207692049	0 37	A G | 3 | G | 0.986105 | - 0 | 0 0 37 0 0 0
	-----------------------
	"""
	DICT=dict()
	with open(ADI) as f:
		for line in f:
			col=line.strip().split()
			pos=col[1]
			genotype=col[9]
			DICT[pos]=genotype
	LIST=DICT.keys()
	return pd.Series(data=[y for x in LIST for y in DICT[x]], index=LIST)

def DF_colPos(BED, TYPE):
	ROW_DATA=pd.read_csv(BED, sep='\t', header=None)
	ROW_DATA[0]=ROW_DATA[0].apply(str)
	ROW_DATA[2]=ROW_DATA[2].apply(str)
	INDEX=ROW_DATA[[0,2]].apply(lambda x: '_'.join(x), axis=1).tolist()

	ANN_INDEX=range(3, len(ROW_DATA.columns))
	if ANN_INDEX:
		for n in ANN_INDEX:
			ROW_DATA[n].index=INDEX

	if TYPE=='col':
		DF=pd.DataFrame(columns=INDEX)
		if ANN_INDEX:
			for n in ANN_INDEX:
				DF.loc["ann_{0}".format(n-2)]=ROW_DATA[n]
	elif TYPE=='row':
		DF=pd.DataFrame(index=INDEX)
		if ANN_INDEX:
			for n in ANN_INDEX:
				DF["ann_{0}".format(n-2)]=ROW_DATA[n]
	return DF

### MAIN ###
def main (PATH, BED):
	TYPE='col'

	FILE_LIST=list()
	for result_path in PATH[0]:
		for (path, dir, files) in os.walk(result_path):
			for file in files:
				if 'adi' in os.path.splitext(file)[-1]:
					FILE_LIST.append(os.path.join(path,file))
	
	if TYPE=='col':
		DF=DF_colPos(BED, TYPE)
		for ADI in FILE_LIST:
			ID=ADI.split('/')[-1].split('.')[0]
			DF.loc[ID,:]=SERIES_selectGenotype(ADI)
	elif TYPE=='row':
		DF=DF_colPos(BED, TYPE)
		for ADI in FILE_LIST:
			ID=ADI.split('/')[-1].split('.')[0]
			DF[ID]=SERIES_selectGenotype(ADI)

	DF.fillna('-', inplace=True)

	writer=pd.ExcelWriter('_genotype.xlsx')
	DF.to_excel(writer, 'genotype')
	writer.save()

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main(argv.path, argv.bed)
	sys.exit(0)