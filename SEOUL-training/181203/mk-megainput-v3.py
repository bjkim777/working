from __future__ import print_function
import os
import sys
import argparse
import subprocess
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

        # rs_map format
        [rs id] [gene syn] [uniprot] [aa change]
        
        ex)
        rs1000000342 ZNF512B Q96KM6 S217T
        rs1000002708 TCF25 Q9H384;Q9BQ70 P572L
	"""
	RS=[]
	S=[]

	# Make sample list (need index number)
	with open(sample) as s:
		for line in s:
			#S.append(line.strip())
			col=line.strip().split()
			S.append(col[-1]+"_"+col[0])

	# Make rs list (need index number)
	with open(ann) as f:
		for line in f:
			col=line.strip().split()
			RS.append(col[4])

	# Action
	DISH={}
	with open(gty) as genotype:
		for s, gn in enumerate(genotype):
			seq=','.join(gn.strip()).split(',')
			SAMPLE=S[s]

			# sequence part
			for i, g in enumerate(seq):

				# change AA
				if g=='2' or g=='3':
					cmd = "grep -w {gene} {ref}".format(gene=RS[i], ref=rs_map)
					rs_amino = os.popen(cmd).readline().strip()
					
					if rs_amino:
						rs  = rs_amino.split()[0]
						u_list = rs_amino.split()[2]
						ref = rs_amino.split()[-1][0]
						alt = rs_amino.split()[-1][-1]
						pos = int(rs_amino.split()[-1][1:-1])-1

						for uniprot in u_list.split(';'):
							# Make Dish
							if uniprot in P:
								DISH[str(SAMPLE)+"_"+uniprot]=copy.deepcopy(P[uniprot])
							
								if DISH[str(SAMPLE)+"_"+uniprot][pos]==ref: 
									front_seq=DISH[str(SAMPLE)+"_"+uniprot][:pos]
									end_seq=DISH[str(SAMPLE)+"_"+uniprot][pos+1:]
									DISH[str(SAMPLE)+"_"+uniprot]=front_seq + alt + end_seq
									
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
		P[header]=seq

	matchGenotype(gty, P, rs_map, ann, sample)	

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main( argv.gty, argv.ref, argv.ann, argv.fasta, argv.sample )
	sys.exit(0)
