import os
import sys
import subprocess
import tempfile
import pandas as pd
import openpyxl # v3.0.3
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Color, colors, Alignment, Border, Side, PatternFill
from datetime import datetime
from natsort import natsorted

def getOpts():
	import argparse
	
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-a', '--arg1', type=str, default='.', metavar='<arg1>',  help= 'description')
	parser.add_argument('-b', '--arg2', type=str, required=True,  metavar= '<arg2>', help= 'description')
	argv = parser.parse_args()
	return(argv)

class STinfo():
	
	TOTAL_HEAD=['Storage', 'Size(TB)', 'Used(TB)', 'Available(TB)', 'Use%','Mounted', \
	'Data List', 'Manager', 'Expiration Date', 'Backup']
	
	HEAD=['Storage', 'Size(TB)', 'Used(TB)', 'Available(TB)', 'Use%','Mounted','Data List']
	CONFIG_FILE='~/.ssh/config'

	def __init__(self, IP):
		self.IP=IP
		self._ssh_client=None

	def LIST_showFolder(self, FOLDER):
		from random import shuffle

		DIR=[ls for ls in os.listdir(FOLDER) if not os.path.isfile(os.path.join(FOLDER, ls))]
		shuffle(DIR)
		if len(DIR)>4:
			DIR=DIR[:4]
		return DIR

	def INS_sshClient(self):
		import paramiko

		self._ssh_client=paramiko.SSHClient()
		ssh_config=paramiko.SSHConfig()
		
		self._ssh_client._policy=paramiko.WarningPolicy()
		self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		user_config_file=os.path.expanduser(self.CONFIG_FILE)
		try:
			with open(user_config_file) as f:
				ssh_config.parse(f)
		except FileNotFoundError:
			print("{} file could not be found. Aborting.".format(user_config_file))
			sys.exit(1)
		
		user_config=ssh_config.lookup(self.IP)
		if 'proxycommand' in user_config:
			user_config['sock']=paramiko.ProxyCommand(user_config['proxycommand'])
			del user_config['proxycommand']
		if 'user' in user_config:
			user_config['username']=user_config['user']
			del user_config['user']

		self._ssh_client.connect(**user_config)
		return self._ssh_client

	def LIST_mahaST(self):
		TOTAL_LIST=[]
		client=self.INS_sshClient()
		stdin, stdout, stderr = client.exec_command('/usr/local/maha/gfs_lsvol -l | awk \'/maha/ {print $(NF-1),$(NF-2),$1}\'')
		for line in [line.strip().split() for line in stdout.readlines()]:
			trans=[]
			for s in line:
				if 'T' in s:
					mu=float(s[:-1])*10**9
					print(mu)
					trans.append(mu)
				elif 'G' in s:
					mu=float(s[:-1])*10*6
					trans.append(mu)
				elif 'M' in s:
					mu=float(s[:-1])*10*3
					trans.append(mu)	
				elif 'K' in s:
					mu=float(s[:-1])
					trans.append(mu)
				else:
					trans.append(s)

			TOTAL_LIST.append([trans[0],trans[1],trans[0]-trans[1],str(trans[1]/trans[0]*100)+'%',trans[-1],''])
		return TOTAL_LIST

def main ():
	A=STinfo(IP='10.0.6.3')
	print(A.LIST_mahaST())
	



if __name__ == "__main__":
	#argv = getOpts()

	main()
	sys.exit(0)