import pandas as pd

def testDataFrame():
	INDEX=[11,22,33,44,55]
	return pd.DataFrame(columns=INDEX)

def testSeries():
	return pd.Series(data=[1,2,3,4])

print (testSeries())
