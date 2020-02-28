import os
import sys
import argparse
import time

def getOpts():
	parser = argparse.ArgumentParser(description = '')
	parser.add_argument('-p', '--path', type=str, default='.', metavar='<path>',  help= 'path to measure size')
	argv = parser.parse_args()
	return(argv)

def diskList(disk):
	DEPTH=6
	DIR={}
	for (path, dir, files) in os.walk(disk):

		if len(path.split('/'))>=DEPTH:
			
			for f in files:
				file=os.path.join(path,f)
				DIR_KEY='/'.join(path.split('/')[0:DEPTH])
				filestat=os.stat(DIR_KEY)
				date=time.strftime('%y%m%d-%H%M%S', time.localtime(filestat.st_mtime))
				size=round(float(os.path.getsize(file))/1024, 2)
				
				if DIR_KEY in DIR:
					DIR[DIR_KEY]+=size
				else:
					DIR[DIR_KEY]=size

			for key in DIR.keys():
				if key[0] is '/':
					filename='/'.join(key.split('/')[2:]).replace('_', '-').replace('.', '-')
				else:
					filename='/'.join(key.split('/')[1:]).replace('_', '-').replace('.', '-')
				print('|{0}|{1}|{2}/|'.format(DIR[key],date,filename))

		else:
			for f in files:
				file=os.path.join(path, f)
				filestat=os.stat(file)
				date=time.strftime('%y%m%d-%H%M%S', time.localtime(filestat.st_mtime))
				size=round(float(filestat.st_size)/1024, 2)
				
				if file[0] is '/':
					filename='/'.join(file.split('/')[2:]).replace('_', '-').replace('.', '-')
				else:
					filename='/'.join(file.split('/')[1:]).replace('_', '-').replace('.', '-')

				print('|{0}|{1}|{2}|'.format(size, date, filename))

def diskList2(disk):
	for (path, dir, files) in os.walk(disk):
		for f in files:
			file=os.path.join(path, f)
			filestat=os.stat(file)
			date=time.strftime('%y%m%d-%H%M%S', time.localtime(filestat.st_mtime))
			size=round(float(filestat.st_size)/1024, 2)

			if size<1:
				continue
			else:
				pass
			
			if file[0] is '/':
				filename='/'.join(file.split('/')[2:]).replace('_', '-').replace('.', '-')
			else:
				filename='/'.join(file.split('/')[1:]).replace('_', '-').replace('.', '-')

			print('|{0}|{1}|{2}|'.format(size, date, filename))

### MAIN ###
def main (disk):
	diskList(disk)

			
### ACTION ### 
if __name__ == "__main__":
	argv = getOpts()

	main( argv.path)
	sys.exit(0)
