#source /tools/.bio_profile ; cd /MDI/1000G-build38/test/chrM ; time python /MDI/1000G-build38/test/makeigdb.py -p 1000G -c chrM -s /MDI/1000G-build38/test/1000g-bam-list -o /MDI/1000G-build38/test

import os
import sys
import subprocess
import shutil
import argparse

PED_PATH='/awork08/IGDB-ann/build38/wes/ped'
RVR='/awork08/kimbj-working/parallel-igds/tools/rvr'
RVR_SEQ='/awork08/kimbj-working/parallel-igds/tools/rvr_seq'
IGDS='/awork08/kimbj-working/parallel-igds/tools/makeIdaInput_v1.0'
IGSCAN='/awork08/kimbj-working/parallel-igds/tools/igscan'

def checkFiles():
	index=0
	for LIST in [PED_PATH, RVR, RVR_SEQ, IGSCAN]:
		if os.path.exists(LIST):
			pass
		else:
			print ('{file} is empty.'.format(file=LIST))
			index+=1
			continue

	if not index==0:
		exit(1)

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-p', '--project', type=str, required=True,  metavar= '<project name>', help= 'project name.\
			Directory in igds library = project.')
	parser.add_argument('-c', '--chr', type=str, required=True,  metavar= '<chromosome>', help= 'chromosome')
	parser.add_argument('-s', '--sample_list', type=str, required=True,  metavar= '<sample list; bam file full path>', help= 'bam file path')
	parser.add_argument('-o', '--output_path', type=str, required=True,  metavar= '<output path>', help= 'output')
	argv = parser.parse_args()
	return(argv)


class MakeIDA:
	def __init__(self, project, chr, sample_list, output_path):
		self.output_path=output_path
		self.chr=chr
		self.project=project
		self.sample_list=sample_list
		self.name_prefix='{project}_{chr}'.format(project=project, chr=chr)

	def searchFile(self):
		for (path, dir, files) in os.walk(self.output_path):
			for file in files:
				if file == 'gtx':
					gtx=os.path.join(path, file)
				elif file == 'dpx':
					dpx=os.path.join(path, file)
				elif file=='key':
					key=os.path.join(path, file)
				elif file=='icx':
					icx=os.path.join(path, file)
				elif file=='gty':
					gty=os.path.join(path, file)
		return [gtx, dpx, key, icx, gty]

	# CKEY
	def makeCkey(self):
		CKEY='{output_path}/{chr}/{name_prefix}.ckey'.format(output_path=self.output_path, chr=self.chr, name_prefix=self.name_prefix)
		CKEY_DP='{output_path}/{chr}/{name_prefix}.dp_ckey'.format(output_path=self.output_path, chr=self.chr, name_prefix=self.name_prefix)

		if os.path.exists(CKEY):
			subprocess.call(['rm', '-f', CKEY])
			subprocess.call(['rm', '-f', CKEY_DP])

		with open(self.sample_list, 'r') as bam_path:
			for line in bam_path:
				sample=line.strip().split('/')[-1].split('.')[0]
				
				with open(CKEY, 'a') as ckey:
					ckey.write('{sample}\n'.format(sample=sample))

				with open(CKEY_DP, 'a') as ckey_dp:
					ckey_dp.write('{sample}_r\n'.format(sample=sample))
					ckey_dp.write('{sample}_a\n'.format(sample=sample))

		return [CKEY, CKEY_DP]


	# PARA
	def makePara(self):
		PARA='{output_path}/{chr}/{name_prefix}.para'.format(output_path=self.output_path, chr=self.chr, name_prefix=self.name_prefix)
		n_sample = sum(1 for line in open(self.sample_list))
		n_marker=sum(1 for line in open(self.searchFile()[2]))

		if os.path.exists(PARA):
			subprocess.call(['rm', '-f', PARA])

		with open(PARA, 'a') as para:
			para.write('#ANN_file {name_prefix}.ann\n'.format(name_prefix=self.name_prefix))
			para.write('#ANN_fields 7\n')
			para.write('#ANN_lines {n_marker}\n'.format(n_marker=n_marker))
			para.write('#PED_file {name_prefix}.ped\n'.format(name_prefix=self.name_prefix))
			para.write('#PED_fields 6\n')
			para.write('#PED_lines {n_sample}\n'.format(n_sample=n_sample))
			para.write('#VAN_file {name_prefix}.van\n'.format(name_prefix=self.name_prefix))
			para.write('#VAN_fields 1\n')
			para.write('#VAN_lines 4\n')
			para.write('#VAR_file {name_prefix}.var\n'.format(name_prefix=self.name_prefix))
			para.write('#VAR_fields 4\n')
			para.write('#VAR_lines {n_sample}\n'.format(n_sample=n_sample))
			para.write('#GTX_file gtx\n')
			para.write('#GTX_chars {n_sample}\n'.format(n_sample=n_sample))
			para.write('#GTX_lines {n_marker}\n'.format(n_marker=n_marker))
			para.write('#GTY_file gty\n')
			para.write('#GTY_chars {n_marker}\n'.format(n_marker=n_marker))
			para.write('#GTY_lines {n_sample}\n'.format(n_sample=n_sample))
		return PARA

	# ANN
	def makeAnn(self):
		ANN='{output_path}/{chr}/{name_prefix}.ann'.format(output_path=self.output_path, chr=self.chr, name_prefix=self.name_prefix)

		if os.path.exists(ANN):
			subprocess.call(['rm', '-f', ANN])

		def decideAlt(self, ref):
			if ref=="A":
				return "T"
			elif ref=="T":
				return "A"
			elif ref=="G":
				return "C"
			elif ref=="C":
				return "G"
			elif ref=="N":
				return "A"

		with open(ANN, 'a') as ann:
			with open(self.searchFile()[2], 'r') as key:
				for index, line in enumerate(key.xreadlines()):
					col=line.strip().split('_')
					chr=col[0]
					pos=col[1]
					ref=col[2]

					ann.write('{chr_pos} Gene_{index} {chr} {pos} none_{index} {ref} {alt}'.format(chr_pos='_'.join(col[0:2]), index=index+1, chr=chr, pos=pos, ref=ref, alt=self.decideAlt(ref)))
		return ANN


	# ------------------------------------ Make DB -----------------------------------------------
	def makeIupacDB(self):
		subprocess.call([RVR_SEQ, '-w', 'seq', self.searchFile()[3], '{output_path}/{name_prefix}.iupac_d'.format(output_path=self.output_path, name_prefix=self.name_prefix), 'rkey_file', self.searchFile()[2], 'ckey_file', self.makeCkey()[0]])

	def makeRv7DB(self):
		subprocess.call([RVR, '-w', 'int', self.searchFile()[1], '{output_path}/{name_prefix}.dp_d'.format(output_path=self.output_path, name_prefix=self.name_prefix), 'ckey_file', self.makeCkey()[1], 'rkey_file', self.searchFile()[2]])

	def makeIGDB(self):
		subprocess.call(['cp', '{igdb_lib}/{project}/{project}.ped'.format(igdb_lib=PED_PATH, project=self.project), '{output_path}/{chr}/{name_prefix}.ped'.format(output_path=self.output_path, chr=self.chr, name_prefix=self.name_prefix)])
		subprocess.call(['cp', '{igdb_lib}/{project}/{project}.var'.format(igdb_lib=PED_PATH, project=self.project), '{output_path}/{chr}/{name_prefix}.var'.format(output_path=self.output_path, chr=self.chr, name_prefix=self.name_prefix)])
		subprocess.call(['cp', '{igdb_lib}/{project}/{project}.van'.format(igdb_lib=PED_PATH, project=self.project), '{output_path}/{chr}/{name_prefix}.van'.format(output_path=self.output_path, chr=self.chr, name_prefix=self.name_prefix)])
		self.makeAnn()

		subprocess.call([IGSCAN, '-s', 'rvrd', self.makePara()])

	# ---------------------------------- Move to finalize -----------------------------------
	def moveToFinalize(self):
		OUTPUT_RV7='{output_path}/RV7'.format(output_path=self.output_path)
		OUTPUT_IUPAC='{output_path}/IUPAC'.format(output_path=self.output_path)
		OUTPUT_IDA='{output_path}/IGDB'.format(output_path=self.output_path)
		OUTPUT_TAR='{output_path}/BACKUP'.format(output_path=self.output_path)
		IUPAC_DB='{output_path}/{name_prefix}.iupac_d'.format(output_path=self.output_path, name_prefix=self.name_prefix)
		RV7_DB='{output_path}/{name_prefix}.dp_d'.format(output_path=self.output_path, name_prefix=self.name_prefix)
		IGDB='{output_path}/{chr}'.format(output_path=self.output_path, chr=self.chr)

		for dir in [OUTPUT_IDA, OUTPUT_RV7, OUTPUT_IUPAC, OUTPUT_TAR]:
			if not os.path.isdir(dir):
				os.mkdir(dir)

		
		for db in [IUPAC_DB, RV7_DB, IGDB]:
			index=0
			if not os.path.isdir(db) or not os.listdir(db):
				print ('{db} is not exist.'.format(db=db))
				index+=1

		if not index==0:
			exit(1)

		# -------------------------------------------------------
		# move outputs
		# -------------------------------------------------------
		shutil.move(IUPAC_DB, OUTPUT_IUPAC)
		shutil.move(RV7_DB, OUTPUT_RV7)
		shutil.move(IGDB, OUTPUT_IDA)

		# -------------------------------------------------------
		# check outputs
		# -------------------------------------------------------
		os.system('sync;sync;sync;sleep 1m')

		os.system('{igscan} -a qc -r {igdb_path}/{chr}/rvr_d mrrn 1 &>/dev/null'.format(igscan=IGSCAN, igdb_path=OUTPUT_IDA, chr=self.chr))		
		os.system('{rvr} -r {rv7_path}/{name_prefix}.dp_d rrrn 1 &>/dev/null'.format(rvr=RVR, rv7_path=OUTPUT_RV7, name_prefix=self.name_prefix))		
		os.system('{rvr} -r {iupac_path}/{name_prefix}.iupac_d rrrn 1 &>/dev/null'.format(rvr=RVR, iupac_path=OUTPUT_IUPAC, name_prefix=self.name_prefix))

		# -------------------------------------------------------
		# tar backup
		# -------------------------------------------------------
		os.system('sync;sync;sync;sleep 1m')

		os.system('tar -cvf {tar_path}/{name_prefix}.iupac_d.tgz \
			--use-compress-prog=pigz \
			-C {iupac_path} \
			$(basename {iupac_path}/{name_prefix}.iupac_d)'.format(iupac_path=OUTPUT_IUPAC, tar_path=OUTPUT_TAR, name_prefix=self.name_prefix))
		os.system('md5sum {tar_path}/{name_prefix}.iupac_d.tgz | sed "s/\(\s\+\).*\//  /" > {tar_path}/{name_prefix}.iupac_d.tgz.md5'.format(tar_path=OUTPUT_TAR, name_prefix=self.name_prefix))

		os.system('tar -cvf {tar_path}/{name_prefix}.dp_d.tgz \
			--use-compress-prog=pigz \
			-C {rv7_path} \
			$(basename {rv7_path}/{name_prefix}.dp_d)'.format(rv7_path=OUTPUT_RV7, tar_path=OUTPUT_TAR, name_prefix=self.name_prefix))
		os.system('md5sum {tar_path}/{name_prefix}.dp_d.tgz | sed "s/\(\s\+\).*\//  /" > {tar_path}/{name_prefix}.dp_d.tgz.md5'.format(tar_path=OUTPUT_TAR, name_prefix=self.name_prefix))

		os.system('tar -cvf {tar_path}/{name_prefix}.igdb.tgz \
			--use-compress-prog=pigz \
			-C {igdb_path} \
			$(basename {igdb_path}/{chr})'.format(igdb_path=OUTPUT_IDA, tar_path=OUTPUT_TAR, name_prefix=self.name_prefix, chr=self.chr))
		os.system('md5sum {tar_path}/{name_prefix}.igdb.tgz | sed "s/\(\s\+\).*\//  /" > {tar_path}/{name_prefix}.igdb.tgz.md5'.format(tar_path=OUTPUT_TAR, name_prefix=self.name_prefix))

### MAIN ###
def main (project, chr, sample_list, output_path):
	checkFiles()
	RUN=MakeIDA(project, chr, sample_list, output_path)

	RUN.makeIupacDB()
	RUN.makeRv7DB()
	RUN.makeIGDB()
	RUN.moveToFinalize()
			

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main(argv.project, argv.chr, argv.sample_list, argv.output_path)
	sys.exit(0)
