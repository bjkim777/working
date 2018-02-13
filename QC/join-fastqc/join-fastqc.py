import os
import sys
import subprocess
import re
import argparse
import locale

locale.setlocale(locale.LC_ALL, '')

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-i', '--input', type=str, required=True,  metavar= '<input>', help= 'input path')
	argv = parser.parse_args()
	return(argv)

def joinFastQC(fastqc_dir):
	FILE={}
	READ={}
	GC={}
	Q30={}
	BASES={}

	print ('#Sample\tTotal_bases\tTotal_reads\tGC(%)\tQ30(%)')
	for (path, dir, files) in os.walk(fastqc_dir):
		for file in files:
			if file == 'fastqc_data.txt':
				FASTQC_DATA=os.path.join(path, file)

				with open(FASTQC_DATA, 'r')	as f:
					for line in f:
						if 'Filename' in line.strip():
							SAMPLE=line.strip().split()[-1].split('_')[0]	# Sample ID :  '_' seperate
							if SAMPLE in FILE:
								FILE[SAMPLE]+=1
							else:
								FILE[SAMPLE]=1
						
						# count Read
						if 'Total Sequences' in line.strip():
							if SAMPLE in READ:
								READ[SAMPLE]+=int(line.strip().split()[-1])
							else:
								READ[SAMPLE]=int(line.strip().split()[-1])
						
						# GC
						p=re.compile('^%GC')
						if p.match(line.strip()):
							if SAMPLE in GC:
								GC[SAMPLE]+=int(line.strip().split()[-1])
							else:
								GC[SAMPLE]=int(line.strip().split()[-1])
			
				# Q30				
				quality=subprocess.Popen(['sed', '-n', '/^>\+Per sequence quality scores\s\+/I,/^>\+/{//d;/^#/d;p}', FASTQC_DATA], stdout=subprocess.PIPE)

				percent30=0
				full=0
				for line in quality.stdout.readlines():
					col=line.strip().split()

					full+=float(col[1])
					if int(col[0]) >= 30:
						percent30+=float(col[1])
				
				if SAMPLE in Q30:
					Q30[SAMPLE]+=(percent30*100/full)
				else:
					Q30[SAMPLE]=(percent30*100/full)

				# count bases
				bases=subprocess.Popen(['sed', '-n', '/^>\+Sequence Length Distribution\s\+/I,/^>\+/{//d;/^#/d;p}', FASTQC_DATA], stdout=subprocess.PIPE)

				count=0
				for line in bases.stdout.readlines():
					col=line.strip().split()
					count+=int(col[0])*float(col[1])

				if SAMPLE in BASES:
					BASES[SAMPLE]+=count
				else:
					BASES[SAMPLE]=count

	keys=FILE.keys()
	keys.sort()

	t_base=0
	t_read=0
	t_q30=0
	t_gc=0
	l_base=[]
	l_read=[]
	l_q30=[]
	l_gc=[]
	for key in keys:
		Q30[key]=Q30[key]/FILE[key]
		GC[key]=GC[key]/FILE[key]

		t_base+=BASES[key]
		t_read+=READ[key]
		t_q30+=Q30[key]
		t_gc+=GC[key]

		l_base.append(BASES[key])
		l_read.append(READ[key])
		l_q30.append(Q30[key])
		l_gc.append(GC[key])


		#print ('{sample}\t{bases}\t{read}\t{gc}\t{q30}'.format(sample=key, bases=format(int(BASES[key]), ',') ,read=format(READ[key], ','), q30=round(Q30[key], 2), gc=GC[key]))  # format(n, ',')
		print ('{sample}\t{bases}\t{read}\t{gc}\t{q30}'.format(sample=key, bases=locale.format('%d', int(BASES[key]), grouping=True) ,read=locale.format('%d', int(READ[key]), grouping=True), q30=round(Q30[key], 2), gc=GC[key]))
	print ('##### Statistic ######')
	print ('#n_of_samples\t{n_sample}'.format(n_sample=len(keys)))
	print ('#Title\tTotal_bases\tTotal_reads\tGC(%)\tQ30(%)')
	print ('Average\t{bases}\t{read}\t{gc}\t{q30}'.format(bases=locale.format('%d', int(t_base/len(keys)), grouping=True), read=locale.format('%d', int(t_read/len(keys)), grouping=True), gc=int(t_gc/len(keys)), q30=round(t_q30/len(keys), 2)))
	print ('Max\t{bases}\t{read}\t{gc}\t{q30}'.format(bases=locale.format('%d', int(max(l_base)), grouping=True), read=locale.format('%d', int(max(l_read)), grouping=True), gc=max(l_gc), q30=round(max(l_q30), 2)))
	print ('Min\t{bases}\t{read}\t{gc}\t{q30}'.format(bases=locale.format('%d', int(min(l_base)), grouping=True), read=locale.format('%d', int(min(l_read)), grouping=True), gc=min(l_gc), q30=round(min(l_q30), 2)))
	


### MAIN ###
def main (input):
	joinFastQC(input)

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main( argv.input )
	sys.exit(0)