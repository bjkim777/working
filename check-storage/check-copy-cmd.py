import os
import sys
import subprocess
import tempfile
import sqlite3

def getOpts():
	import argparse
	
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-d', '--db', type=str, default='cp-cmd.db', metavar='<arg1>',  help= 'sqlite3 db path')
	argv = parser.parse_args()
	return(argv)

def LIST_findCopy():
	# [['1591774045', '6948', '0', ['cp', '/data2/DATA/fastq/ST-753_2.fastq.gz', '/dev/null']]]
	TOTAL=[]
	command_line=\
	'ps  -eo lstart,pid,etimes,cmd | \
	grep -P "\\sscp\\s|\\scp\\s|\\srsync\\s" | \
	awk \'{ \
		cmd="date -d\\""$1 FS $2 FS $3 FS $4 FS $5"\\" +\\"%s\\""; \
		cmd | getline d; \
		close(cmd); \
		$1=$2=$3=$4=$5=""; \
		printf "%s\\n",d$0 \
	}\''
	
	for line in subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE).stdout.readlines():
		tmp=line.strip().decode('utf-8').split()
		tmp2=tmp[0:3]
		tmp2.append(tmp[3:])
		TOTAL.append(tmp2)
	return TOTAL

def TUPLE_hddSN(dev='/dev/sda1'):
	# ('/dev/sda1', '39J0A008FKRE')
	command_line=\
	'udevadm info --query=all --name={0} | grep ID_SERIAL_SHORT'.format(dev)

	result=subprocess.Popen(command_line, 
		shell=True, 
		stdout=subprocess.PIPE, 
		stderr=subprocess.PIPE)
	std_out, std_err = result.communicate()
	SN=std_out.strip().decode('utf-8').split('=')[-1]
	if SN=='':
		SN='-'
	return dev, SN
	
def DIC_mountList():
	# {'/': '/dev/sdb2', '/boot/': '/dev/sdb1', '/data/': '/dev/sdc1', '/home/': '/dev/sdb5', '/data2/': '/dev/sda1'}
	MOUNT={}
	command_line='df | sed 1d'

	for line in subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE).stdout.readlines():
		tmp=line.strip().decode('utf-8').split()
		if not 'tmpfs' in tmp[0]:
			if tmp[-1]!='/':
				MOUNT[tmp[-1]+'/']=tmp[0]
			else:
				MOUNT[tmp[-1]]=tmp[0]
	return MOUNT

def LIST_formatingDev(findCopy, mountList):
	TOTAL=[]
	HOSTNAME=subprocess.Popen('hostname', \
		shell=True, \
		stdout=subprocess.PIPE).\
		stdout.readlines()[0].decode('utf-8').strip()
	IP=subprocess.Popen('hostname -I', \
		shell=True, \
		stdout=subprocess.PIPE).\
		stdout.readlines()[0].decode('utf-8').strip().split()[0]
	MOUNT=mountList.keys()

	for ps in findCopy:
		target=[]
		target2=[]
		count=0
		for component in ps[-1]:
			if '/' in component:
				count+=1
				if os.path.isdir(component):
					component=component+'/'
				for dev in MOUNT:
					if dev=='/':
						pass
					else:
						if dev in component:
							target.append(dev)
							target2.append(component)

				if len(target)!=count:
					target.append('/')

		TOTAL.append([
			'{0}_{1}'.format(ps[0], ps[1]), \
			'{0}({1})'.format(HOSTNAME, IP), \
			','.join(list(map(lambda x: mountList[x], target[0:-1]))), \
			','.join(target[0:-1]), \
			','.join(target2[0:-1]), \
			mountList[target[-1]], \
			target[-1], \
			TUPLE_hddSN(dev=mountList[target[-1]])[-1], \
			ps[0], \
			ps[2], \
			' '.join(ps[-1])])
	return TOTAL

def main (db):
	DATA=\
	LIST_formatingDev(\
		LIST_findCopy(), \
		DIC_mountList() \
		)
	TABLE='copy2'

	conn=sqlite3.connect(db)
	cur=conn.cursor()

	sql_create_table=\
		"""CREATE TABLE IF NOT EXISTS {0}(
				ID text PRIMARY KEY,
				HOST text,
				INDEV text,
				INMOUNT text,
				DATA text,
				OUTDEV text,
				OUTMOUNT text,
				OUTSN text,
				STIME integer,
				ETIME integer,
				CMD text
			); """.format(TABLE)
	cur.execute(sql_create_table)

	for line in DATA:
		try:
			sql=\
			"INSERT INTO \
				{0} ( \
					ID, \
					HOST, \
					INDEV, \
					INMOUNT, \
					DATA, \
					OUTDEV, \
					OUTMOUNT, \
					OUTSN, \
					STIME, \
					ETIME, \
					CMD) VALUES (?,?,?,?,?,?,?,?,?,?,?);".format(TABLE)
			cur.execute(sql,line)

		except Exception as e:
			sql="UPDATE {0} SET ETIME=? WHERE ID=?;".format(TABLE)
			cur.execute(sql,[line[-2],line[0]])

	conn.commit()
	conn.close()

if __name__ == "__main__":
	argv = getOpts()

	main(db=argv.db)
	sys.exit(0)