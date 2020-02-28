import os
import sys
import subprocess
import tempfile
import argparse
import sqlite3

def GetOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('action', type=str, required=True,  metavar= '<search or insert>', help= 'search or insert')
	parser.add_argument('-d', '--db', type=str, required=True, metavar='<database file>',  help= 'database file')
	parser.add_argument('-s', '--string', type=str, metavar='<inserted file or target word>',  help= 'text file or word')
	argv = parser.parse_args()
	return(argv)

def InputData():
	a

def Search(db, target):
	conn = sqlite3.connect(db)

	with conn:
		cur = conn.cursor()
		sql = 'select ? from *'
		cur.execute(sql, (target))
		rows = cur.fetchall()
		for row in rows:
			print(row)

def Insert(db, target):
	conn = sqlite3.connect(db)

	with conn:
		cur = conn.cursor()
		sql = 'insert into '

### MAIN ###
def main (db, action, target):
	if action == 'search':
		Search(db, target)
	elif action == 'insert':
		Insert(db,target)
	else:
		print (' %s is not option.',action)
		exit(1)


### ACTION ### 
if __name__ == "__main__":
	argv = GetOpts()

	main(argv.db, argv.action, argv.target)
	sys.exit(0)