#x[NR]=$2 : Store ID
awk -F"/" '{ x[NR]=$2 } END {for (i in x) { printf x[i]"_type1\t"x[i]"score1\t"x[i]"_type2\t"x[i]"_score2\t"}}'  $1