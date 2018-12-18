from __future__ import print_function
import sys
import argparse
from itertools import groupby
import copy

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-g', '--gty', type=str, required=True,  metavar= '<igscan gty>', help= 'genotype')
	parser.add_argument('-f', '--fasta', type=str, required=True,  metavar= '<fasta>', help= 'protein seqence : fasta')
	parser.add_argument('-r', '--ref', type=str, required=True,  metavar= '<ref>', help= 'rs mapping table')
	parser.add_argument('-a', '--ann', type=str, required=True,  metavar= '<igscan ann>', help= 'igscan ann format')
	parser.add_argument('-s', '--sample', type=str, required=True,  metavar= '<skey>', help= 'igscan skey format')
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

def matchGenotype(gty, P, rs_map, ann, sample):
	"""
	# gty format
	row : sample
	column : position

	# P is protein sequence's dictionary.

	# ann format
	----------
	[chr_pos] [gene syn] [chr] [pos] [rs] [ref allele] [alt allele]

	ex)
	chr1_17308197 PADI4 chr1 17308197 rs372899755 A G
	
	# sample is skey. num of gty's row = num of skey's row
	"""
	RS=[]
	UNP=set()
	S=[]
	RS_UNP={}
	RS_AA={}

	def rsMapping(rs_map):
		"""
	        # rs_map format
	        [rs id] [gene syn] [uniprot] [aa change]
        
        	ex)
	        rs1000000342 ZNF512B Q96KM6 S217T
	        rs1000002708 TCF25 Q9H384;Q9BQ70 P572L
		"""
		with open(rs_map) as data:
			for line in data:
				yield line.strip().split()
	# Make sample list (need index number)
	with open(sample) as s:
		for line in s:
			#S.append(line.strip())
			col=line.strip().split()
			S.append(col[-1]+"_"+col[0])

	# Make mapping table	
	for rs, gyn, unprot, aa in rsMapping(rs_map):
		RS_UNP[rs]=unprot
		RS_AA[rs]=aa

	# Make rs list (need index number)
	with open(ann) as f:
		for line in f:
			col=line.strip().split()
			RS.append(col[4])

	# Make uniprot list
	for rs in RS:
		if rs in RS_UNP:
			for uniprot in RS_UNP[rs].split(';'):
				UNP.add(uniprot)

	# Action
	DISH={}
	with open(gty) as genotype:
		for s, gn in enumerate(genotype):
			seq=','.join(gn.strip()).split(',')
			SAMPLE=S[s]

			# make dish
			for uniprot in UNP:
				if str(SAMPLE)+"_"+uniprot in DISH:
					pass
				else:
					if uniprot in P:
						DISH[str(SAMPLE)+"_"+uniprot]=copy.deepcopy(P[uniprot])
			# sequence part
			for i, g in enumerate(seq):

				# change AA
				if g=='2' or g=='3':
					
					if RS[i] in RS_AA:
						ref = RS_AA[RS[i]][0]
						alt = RS_AA[RS[i]][-1]
						pos = int(RS_AA[RS[i]][1:-1])-1
						
						for uniprot in RS_UNP[RS[i]].split(';'):
							if str(SAMPLE)+"_"+uniprot in DISH:
								if DISH[str(SAMPLE)+"_"+uniprot][pos]==ref: 
									DISH[str(SAMPLE)+"_"+uniprot][pos]=alt
								else:
									print ("{uni} : {rs} : {aa}, {id}".format(id=str(SAMPLE)+"_"+uniprot ,uni=uniprot,rs=RS[i], aa=RS_AA[RS[i]]), file=sys.stderr)
									raise Exception("Amino acid not match.")
					else:
						#print("{rs} is not match uniprot table".format(rs=RS[i]), file=sys.stderr)
						pass
	# Print fasta
	for key in DISH.keys():
		print(">{key}".format(key=key))
		print("".join(DISH[key]))
			
### MAIN ###
def main (gty, rs_map, ann, fasta, sample):
	P={}

	# sequnece dic
	f=fasta_iter(fasta)
	for header, seq in f:
		P[header]=','.join(seq).split(',')

	matchGenotype(gty, P, rs_map, ann, sample)	

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main( argv.gty, argv.ref, argv.ann, argv.fasta, argv.sample )
	sys.exit(0)
