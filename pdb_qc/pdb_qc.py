import os
import sys
import subprocess
import tempfile
import argparse

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-p', '--pdb', type=str, required=True,  metavar= '<pdb>', help= 'input pdb')
	argv = parser.parse_args()
	return(argv)

def BOOLEAN_pdbQC(pdb):
	"""True is error, False is not error."""

	target1='grep \"\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\\*\" %s'%(pdb)
	target2='grep \"\\-nan\" %s'%(pdb)

	def _convertCmdtoBool(*cmds):
		check=set()
		for cmd in cmds:
			b=bool(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.readlines())
			check.add(b)
		for i,c in enumerate(list(check)):
			if i==0:
				result=c
			else:
				result=result or c
		return result

	return _convertCmdtoBool(target1, target2)

### MAIN ###
def main (pdb):

	if BOOLEAN_pdbQC(pdb):
		print('error: %s'%(pdb))
	else:
		print('QC pass: %s'%(pdb))
			

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main( argv.pdb)
	sys.exit(0)