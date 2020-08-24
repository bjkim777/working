import os
import sys
import subprocess
import tempfile
import argparse
import pandas as pd
import sqlite3

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-p', '--path', type=str, required=True, metavar= '<parent directory path>', help= """input parent directory path 
		with \'DARC/pdb\' and \'RLDENVA/env_out\'""")
	parser.add_argument('-d', '--db', type=str, default='khit-status.sql', metavar= '<sqlite db>', help= 'sqlite db')
	argv = parser.parse_args()
	return(argv)

class KHIT_status():
	def __init__(self, PATH):
		self._path=PATH

	def DF_final(self):
		PDB_DIR=self._path+'/DARC/pdb'
		TAR_DIR=self._path+'/RLDENVA/env_out'

		if os.path.isdir(PDB_DIR):
			command_line='find {0} -name  \'*.pdb\' | sort'.format(PDB_DIR)
			DF_GPU=self._DF_targetStatus(self._LIST_fileList(command_line))
		else:
			raise Exception('\'{0}\' not found.'.format(PDB_DIR))
		if os.path.isdir(TAR_DIR):
			command_line='find {0} -name  \'*.tar.gz\' | sort'.format(TAR_DIR)
			DF_CPU=self._DF_targetStatus(self._LIST_fileList(command_line))
		else:
			# print('You must make \'{0}\' later. Now, I will make empty Dataframe.'.format(TAR_DIR))
			DF_CPU=pd.DataFrame()

		return DF_GPU, DF_CPU
		

	def _LIST_fileList(self, command_line):
		LIST=[]
		for line in subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE).stdout.readlines():
			FILE=line.strip().decode('utf-8')
			LIST.append(FILE)
		return LIST

	def _DF_targetStatus(self, LIST_FILELIST):
		"""
		ex)
		                AAAA  AAAB  AAAC
		CDK7_1ua2A_ATP     1     1     0
		FLT3_4rt7A         0     1     0
		FLT3_4xufA         0     1     1
		"""
		DICT={}
		COL=set()

		for line in LIST_FILELIST:
			col=line.split('/')[-1].split('.')[0].split('_')
			GENE_CHAIN='{0}_{1}'.format(col[0],'_'.join(col[1:-3]))
			COMPOUND=col[-1]

			COL.add(COMPOUND)

			if GENE_CHAIN in DICT:
				if COMPOUND in DICT[GENE_CHAIN]:
					DICT[GENE_CHAIN][COMPOUND]+=1
				else:
					DICT[GENE_CHAIN][COMPOUND]=1
			else:
				DICT[GENE_CHAIN]={COMPOUND:1}

		SORT=list(COL); SORT.sort()
		BOX=pd.DataFrame(columns=SORT)

		for gene_chain in DICT.keys():
			msg=pd.Series(DICT[gene_chain])
			BOX.loc[gene_chain]=msg
		BOX.fillna(0, inplace=True)

		return BOX.astype(int)


### MAIN ###
def main (DIR, DB):
	KHIT=KHIT_status(DIR)
	DF_GPU, DF_CPU=KHIT.DF_final()
	TABLE=['DARC', 'DM']

	conn=sqlite3.connect(DB)

	for i, step in enumerate(TABLE):
		if i==0: DF=DF_GPU.T
		else: DF=DF_CPU.T

		try:
			DF.to_sql(step, conn, chunksize=100000)
		except:
			cur=conn.cursor()
			cur.execute('SELECT "index" FROM "{0}";'.format(step))
			INDEX=set([x[0] for x in cur.fetchall()])
			if len(INDEX)==0:
				DF.to_sql(step, conn, if_exists='replace', chunksize=100000)
				continue
			INDEX_df=set(DF.index.to_list())
			APPEND=list(INDEX_df-INDEX); APPEND.sort()

			cur.execute('PRAGMA TABLE_INFO("{0}")'.format(step))
			HEAD= set([x[1] for x in cur.fetchall()][1:])
			HEAD_df=set(DF.columns.to_list())

			for head in list(HEAD_df-HEAD):
				cur.execute('ALTER TABLE "{0}" ADD COLUMN "{1}" INTEGER;'.format(step,head))
				for index in list(INDEX):
					if index in INDEX_df:
						cur.execute('UPDATE "{0}" SET "{1}"={2} WHERE "index"="{3}";'.format(step, head, DF[head].loc[index], index))
					else:
						cur.execute('UPDATE "{0}" SET "{1}"={2} WHERE "index"="{3}";'.format(step, head, 0, index))

			if not APPEND:
				continue
			else:
				ADD=DF.loc[APPEND]
				for add in list(HEAD-HEAD_df):
					ADD[add]=0
				ADD.to_sql(step, conn, if_exists='append', chunksize=100000)

			conn.commit()
			

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main( DIR=argv.path, DB=argv.db  )
	sys.exit(0)