import os
import sys
import subprocess
import tempfile
import argparse

SAMPLE={}
TYPE={}

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-l', '--list', type=str, required=True,  metavar= '<hla report list>', help= 'hla report list')
	argv = parser.parse_args()
	return(argv)

def collectTYPE(hla):
	col=hla.split('/')[-1].split('.')
	sample=col[0]
	gene=col[1]
	sample_gene='{sample}_{gene}'.format(sample=sample, gene=gene)

	if str(sample) in SAMPLE:
		SAMPLE[str(sample)].add(str(sample_gene))
	else:
		SAMPLE[str(sample)]=set([str(sample_gene)])
	"""
	sample dic

	ex)
	NA18971 : NA18971_HLA-A
	"""

	if str(sample_gene) in TYPE:
		pass
	else:
		TYPE[str(sample_gene)]=[]
	"""
	type dic

	ex)
	NA18971_HLA-A : ['52:01:01:01', '44:03:01']
	"""

	with open(hla, 'r') as f:
		for line in f:
			if '[Type 1]' in line.strip():
				TYPE[str(sample_gene)].append(str(line.strip().split()[2]))

			if '[Type 2]' in line.strip():
				TYPE[str(sample_gene)].append(str(line.strip().split()[2]))

	if len(TYPE[str(sample_gene)]) == 2:
		pass
	elif len(TYPE[str(sample_gene)]) == 1:
		TYPE[str(sample_gene)].append('None')
	elif len(TYPE[str(sample_gene)]) == 0:
		TYPE[str(sample_gene)].append('None')
		TYPE[str(sample_gene)].append('None')

### MAIN ###
def main (file_list):
	with open(file_list, 'r') as files:
		for file in files:
			collectTYPE(file.strip())

	# ---------------------------
	# make head
	# ---------------------------
	tmp=set()
	head=[]	
	for sample in SAMPLE.keys():
		gene_list=list(SAMPLE[str(sample)])
		gene_list.sort()

		for sample_gene in gene_list:
			gene=sample_gene.split('_')[-1]
			tmp.add(gene)
		tmp2=list(tmp)
		tmp2.sort()

	for gene in tmp2:
		head.append(str(gene)+'.type1')
		head.append(str(gene)+'.type2')
	head.insert(0,'sample')

	print '\t'.join(head)

	# ---------------------------
	# print type
	# ---------------------------
	for sample in SAMPLE.keys():
		gene_list=list(SAMPLE[str(sample)])
		gene_list.sort()


		printer=[sample]
		for gene in gene_list:
			printer.append('\t'.join(TYPE[str(gene)]))
		print '\t'.join(printer)
			

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main(argv.list)
	sys.exit(0)