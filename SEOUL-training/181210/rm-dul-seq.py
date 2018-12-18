from __future__ import print_function
import sys
import argparse
from itertools import groupby

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-u', '--uc', type=str, required=True,  metavar= '<uc>', help= 'uc')
	parser.add_argument('-f', '--fasta', type=str, required=True,  metavar= '<fasta>', help= 'fasta')
	argv = parser.parse_args()
	return(argv)

def fasta_iter(fasta):
        """
        given a fasta file. yield tuples of header, sequence
        """
	with open(fasta) as fh:
        # ditch the boolean (x[0]) and just keep the header or sequence since
        # we know they alternate.
		faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
		for header in faiter:
                        # drop the ">"
			header = header.next()[1:].strip()
                        # join all sequence lines to one.
			seq = "".join(s.strip() for s in faiter.next())
			yield header, seq

def removeKey(DIC):
	NUMofRACE=26
	MSG=['-',0]
		
	for key in DIC.keys():
		if MSG[-1]<len(DIC[key]):
			MSG=[key,len(DIC[key])]

	if len(set(map(lambda x : x.split('_')[0], DIC[MSG[0]]))) >= NUMofRACE:
		DIC.pop(MSG[0],None)
		removeKey(DIC)

	return set([y for x in DIC.keys() for y in DIC[x]])

### MAIN ###
def main (uc,fasta):
	P={}
	DISH={}
	
	with open(uc) as f:
		for line in f:
			col=line.strip().split()
			if col[-1]=='*' and col[0]!="C":
				if col[-2] in DISH: pass
				else: DISH[col[-2]]=[col[-2]]
			elif col[0]=="C": pass
			else:
				DISH[col[-1]].append(col[-2])

	for header, seq in fasta_iter(fasta):
		if header in removeKey(DISH):
			P[header]=seq
	
	for key in P.keys():
		fasta = "{0}_{1}.fa".format(key.split('_')[0], key.split('_')[-1])
		with open(fasta, 'a') as f:
			f.write(">{0}\n".format(key))
			f.write(P[key]+'\n')

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main( argv.uc, argv.fasta )
	sys.exit(0)
