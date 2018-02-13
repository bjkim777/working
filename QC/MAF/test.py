import sys

script, file1=sys.argv
sum1=0
sum2=0
sum3=0
sum4=0
sum5=0
sum6=0
sum7=0
sum8=0
sum9=0
sum10=0
with open(file1, 'r') as f:

	for line in f:
		dp=line.strip().split()[0]
		maf=line.strip().split()[1]

		if maf > 0.1:
			if dp <=100:
				sum1+=int(1)
			if dp<=200:
				sum2+=int(1)
			if dp<=300:
				sum3+=int(1)
			if dp<=400:
				sum4+=int(1)
			if dp<=500:
				sum5+=int(1)
			if dp<=600:
				sum6+=int(1)
			if dp<=700:
				sum7+=int(1)
			if dp<=800:
				sum8+=int(1)
			if dp<=900:
				sum9+=int(1)
			if dp<=1000:
				sum10+=int(1)

print sum1, sum2,sum3,sum4,sum5,sum6,sum7,sum8,sum9,sum10