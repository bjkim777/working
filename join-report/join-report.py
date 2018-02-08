"""
This version worked duplication first column.
"""
# join -j1 -t$'\t' -a1 -a2 -e- -o0 1.2 1.3 1.4 1.5 2.2 2.3 2.4 2.5 [file1] [file2] 
import sys
import subprocess
import tempfile

def JoinReport(file1 , file2 , index):
	if file1 == 1 :
		temp = tempfile.NamedTemporaryFile(delete=False, bufsize=1)
		with open(file2 , 'r') as buf :
			for line in buf.readlines() :
				temp.write(line)
		#print temp.name
		return temp

	else :
		col="1.2 "
		"""
		1st : 1.2	1.3	1.4	1.5
		2nd : 1.2	1.3	1.4	1.5	1.6	1.7	1.8	1.9
		3rd : 1.2	1.3	1.4	1.5	1.6	1.7	1.8	1.9	1.10	1.11	1.12	1.13
		4th : 1.2	1.3	1.4	1.5	1.6	1.7	1.8	1.9	1.10	1.11	1.12	1.13	1.14	1.15	1.16	1.17
		"""
		for num in range(3 ,int(index)*4+2) : 			# 4n + 2 : column index
			col+= "1." + str(num) + " "

		join = subprocess.Popen(['join','-j1','-t','\t','-a1','-a2','-e-','-o0',col.strip(),'2.2','2.3','2.4','2.5',file1,file2], stdout=subprocess.PIPE)
		temp = tempfile.NamedTemporaryFile(delete=False,bufsize=1)

		for line in join.stdout.readlines() :
			temp.write(line)
		subprocess.call(['rm','-f',file1])
		#print temp.name
		return temp

def RowtoColumn(TOTAL):

	tmp=subprocess.Popen([
		'awk', '{ \
			for (col=1; col<=(NF-1)/4; col++) \
				{ out[NR,col]=$(col*4-2)]"\\t"$(col*4-1)"\\t"$(col*4)"\\t"$(col*4+1) } \
				if (big<=(NF-1)/4) big=(NF-1)/4 } \
			END { \
				for (i=1; i<=big; i++) { \
					for (j=1; j<=NR; j++) { \
							prinf ("%s\\t", out[j,i])  \
							} \
						printf "\\n"  \
						} \
					}' , str(TOTAL)], stdout=subprocess.PIPE)

	CTOR = str(TOTAL)+"-ctor"
	with open(CTOR,'w') as f:
		for line in tmp.stdout.readlines():
			f.write(line)

	return CTOR


### MAIN ###
def main (file_list):

	count = subprocess.Popen(['wc','-l',file_list] , stdout = subprocess.PIPE).stdout.readlines()[0].strip().split()[0]
	
	with open(file_list , 'r') as index:
		TMP = {}
		for num , file in enumerate(index.readlines()) :
			print str(int(num)+1),file.strip()
			if num == 0 :
				TMP[num] = JoinReport(file1= 1, file2=file.strip(), index = num).name
				
			elif num == int(count) -1 :
				TMP[num] = JoinReport(file1 = TMP[num-1], file2 = file.strip() , index = num).name
				
				with open(file_list + '.total' , 'w') as total :
					with open(TMP[num] , 'r') as  temp :
						for line in temp.readlines() :
							total.write(line)

				subprocess.call(['rm','-f',TMP[num]])
				
			else :
				TMP[num] = JoinReport(file1 = TMP[num-1], file2 = file.strip() , index = num).name

	#RowtoColumn(total)


### ACTION ### 
if __name__ == "__main__":
	if len(sys.argv) == 2:
		 file_list= sys.argv[1]
	else:
		sys.stderr.write(
"Usage : "+sys.argv[0]+" [file list]\n"
)
		sys.exit(1)

	main( file_list )
	sys.exit(0)
