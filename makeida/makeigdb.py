# Add part of make IGDB input files
# need pigz
# Don't use relative path

from __future__ import print_function	# print stderr 
import os
import sys
import subprocess
import shutil						# move directory
import argparse


PED_PATH='/awork08/IGDB-ann/build38/wes/ped'
RVR='/awork08/kimbj-working/parallel-igds/tools/rvr'
RVR_SEQ='/awork08/kimbj-working/parallel-igds/tools/rvr_seq'
IGDS='/awork08/kimbj-working/parallel-igds/tools/makeIdaInput_v1.0'
IGSCAN='/awork08/kimbj-working/parallel-igds/tools/igscan'
REF='/awork08/BUILD38-SOURCE/build38-1000g-ref/GRCh38_full_analysis_set_plus_decoy_hla.fa'
TOOL_SOURCE='/tools/.bio_profile'

def source(script, update=1):
	pipe = subprocess.Popen(". %s; env" % script, stdout=subprocess.PIPE, shell=True)
	data = pipe.communicate()[0]

	env = dict((line.split("=", 1) for line in data.splitlines()))
	if update:
		os.environ.update(env)

	return env

def checkFiles(bam_list):
	SAMPLE={}
	index=0
	for LIST in [PED_PATH, RVR, RVR_SEQ, IGDS, IGSCAN, REF, TOOL_SOURCE]:
		if os.path.exists(LIST):
			pass
		else:
			print ('{file} is not exist.'.format(file=LIST), file=sys.stderr)
			index+=1

	with open(bam_list, 'r') as f:
		for line in f:
			sample=line.strip().split('/')[-1].split('.')[0]

			# check size
			if os.path.getsize(line.strip()) <= 1048576: # 1MB
				print ('{file} is empty.'.format(file=line.strip()), file=sys.stderr)
				index+=1
			
			# check duplication
			if str(sample) in SAMPLE:
				SAMPLE[str(sample)]+=1
			else:
				SAMPLE[str(sample)]=1
		
	if not index==0:
		raise Exception('Files are not exist or empty.')

	dul=0
	for i, key in enumerate(SAMPLE.keys()):
		if not SAMPLE[str(key)] is 1:
			print (key, file=sys.stderr)
			dul+=1

	if not dul==0:
		raise Exception('duplication')


def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-p', '--project', type=str, required=True,  metavar= '<project name>', help= 'project name.\
			Directory in igds library = project.')
	parser.add_argument('-b', '--bed', type=str, required=True,  metavar= '<bed file>', help= 'bed')
	parser.add_argument('-s', '--sample_list', type=str, required=True,  metavar= '<sample list; bam file full path>', help= 'bam file path')
	parser.add_argument('-o', '--output_path', type=str, required=True,  metavar= '<output path>', help= 'output')
	argv = parser.parse_args()
	return(argv)


class MakeIDA:
	def __init__(self, project, bed, sample_list, output_path):
		self.output_path=output_path
		self.bed=bed
		self.project=project
		self.sample_list=sample_list
		self.name_prefix='{project}_{chr}'.format(project=project, chr=bed.split('/')[-1].split('.bed')[0])
		self.chr=bed.split('/')[-1].split('.bed')[0]

	def makeInput(self):
		OUTPUT='{output_path}/{chr}'.format(output_path=self.output_path, chr=self.chr)

		if not os.path.isdir(OUTPUT):
			os.mkdir(OUTPUT)

		subprocess.call([IGDS, '-l', self.sample_list, '-r', REF, '-o', OUTPUT, '-b', self.bed])

	def searchFile(self):
		for (path, dir, files) in os.walk(self.output_path + "/" + self.chr):
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
		n_van_line=sum(1 for line in open('{igdb_lib}/{project}/{project}.van'.format(igdb_lib=PED_PATH, project=self.project)))

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
			para.write('#VAN_lines {0}\n'.format(n_van_line))
			para.write('#VAR_file {name_prefix}.var\n'.format(name_prefix=self.name_prefix))
			para.write('#VAR_fields {0}\n'.format(n_van_line))
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

		def decideAlt(ref):
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
					chr='_'.join(col[0:-2])
					pos=col[-2]
					ref=col[-1]

					ann.write('{chr_pos} Gene_{index} {chr} {pos} none_{index} {ref} {alt}\n'.format(chr_pos=str(chr)+'_'+str(pos), index=index+1, chr=chr, pos=pos, ref=ref, alt=decideAlt(ref)))
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
		
		os.chdir('{output_path}/{chr}'.format(output_path=self.output_path,chr=self.chr))
		# need 'source /tools/.bio_profile'
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
		
		# -------------------------------------------------------
		# check outputs
		# -------------------------------------------------------
		os.system('sync;sync;sync;sleep 1m')

		check_igdb=subprocess.Popen([IGSCAN, '-a', 'qc', '-r', IGDB+'/'+'rvr_d', 'mrrn', '1'], stdout=subprocess.PIPE).stdout.readlines()[0]
		check_rv7=subprocess.Popen([RVR, '-r', RV7_DB,'rrrn', '1'], stdout=subprocess.PIPE).stdout.readlines()[0]
		check_iupac=subprocess.Popen([RVR, '-r', IUPAC_DB, 'rrrn', '1'], stdout=subprocess.PIPE).stdout.readlines()[0]

		index=0
		for db in [IUPAC_DB, RV7_DB, IGDB]:
			if not os.path.isdir(db) or not os.listdir(db):
				print ('{db} is not exist.'.format(db=db), file=sys.stderr)
				index+=1

		if not index is 0:
			raise Exception('DB is not exist.')

		empty=0
		for result in [[str(check_igdb), str(IGDB+'/'+'rvr_d')], [str(check_iupac), str(IUPAC_DB)], [str(check_rv7), str(RV7_DB)]]:
			if '\x00' in result[0]:	# empty line
				print ('{db} is empty.'.format(db=result[1]), file=sys.stderr)
				empty+=1

		if not empty is 0:
			raise Exception('DB is empty.')

		# -------------------------------------------------------
		# move outputs
		# -------------------------------------------------------
		shutil.move(IUPAC_DB, OUTPUT_IUPAC)
		shutil.move(RV7_DB, OUTPUT_RV7)
		shutil.move(IGDB, OUTPUT_IDA)

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
def main (project, bed, sample_list, output_path):
	checkFiles(sample_list)
	
	# ENV PATH
	source(TOOL_SOURCE)

	RUN=MakeIDA(project, bed, sample_list, output_path)
	
	RUN.makeInput()
	RUN.makeIupacDB()
	RUN.makeRv7DB()
	RUN.makeIGDB()
	RUN.moveToFinalize()
			

### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main(argv.project, argv.bed, argv.sample_list, argv.output_path)
	sys.exit(0)
