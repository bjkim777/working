## objective: find sequences that all 26 races have in common

import re
import pandas as pd

## separate dataframe for each protein
df_DHFR = pd.read_table('01_ALL_DHFR.fasta.uc', delim_whitespace=True, header = None)
df_NQO2 = pd.read_table('01_ALL_NQO2.fasta.uc', delim_whitespace=True, header = None)
df_PSAT1 = pd.read_table('01_ALL_PSAT1.fasta.uc', delim_whitespace=True, header = None)

## data frame subsetting
## exclude rows with 'C' as first column
## only take the last two columns, which have relevant information
def handling(data_frame):
    data_frame.reset_index(drop=True, inplace=True)
    data_frame.columns = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth']
    data_frame.head()
    # eliminate rows with 'C' in the first column
    data_frame = data_frame[data_frame['first'] != 'C']
    interest = data_frame[['ninth', 'tenth']].copy()
    interest = interest.reset_index()
    return interest

## call data handling function on all three dataframes
DHFR = handling(df_DHFR)
NQO2 = handling(df_NQO2)
PSAT1 = handling(df_PSAT1)

## 26 races
races = ["ACB", 'ASW', 'BEB', "CDX", "CEU", "CHB", "CHS", "CLM", "ESN", "FIN", "GBR", "GIH",
         "GWD", "IBS", "ITU", "JPT", "KHV", "LWK", "MSL", "MXL", "PEL", "PJL", "PUR", "STU", "TSI", "YRI"]

## find the starred sequences (star indicates start of a cluster)
def locs(data_frame):
    loc_df = data_frame.loc[data_frame['tenth'] == '*']
    return loc_df

## get the row indeces of the start and end of each cluster
def row_pairs(data_frame):
    rows = locs(data_frame).index.values.tolist()
    row_pairs_list = [(rows[i],rows[i+1]) for i in range(0,len(rows) -1)]
    return row_pairs_list

## call row-indeces function on all three subsetted dataframes
DHFR_rowpairs = row_pairs(DHFR)
NQO2_rowpairs = row_pairs(NQO2)
PSAT1_rowpairs = row_pairs(PSAT1)

## check whether all 26 races are represented in a cluster
def check_all_races(data, row_pairs):
    all_races_common_sequence = []

    for i in row_pairs:
        start_index = i[0]
        end_index = i[1]
        df_temp = data[start_index:end_index]
        series_raceinfo = df_temp['ninth']

        ACB_check = any(series_raceinfo.str.contains('ACB'))
        ASW_check = any(series_raceinfo.str.contains('ASW'))
        BEB_check = any(series_raceinfo.str.contains('BEB'))
        CDX_check = any(series_raceinfo.str.contains('CDX'))
        CEU_check = any(series_raceinfo.str.contains('CEU'))
        CHB_check = any(series_raceinfo.str.contains('CHB'))
        CHS_check = any(series_raceinfo.str.contains('CHS'))
        CLM_check = any(series_raceinfo.str.contains('CLM'))
        ESN_check = any(series_raceinfo.str.contains('ESN'))
        FIN_check = any(series_raceinfo.str.contains('FIN'))
        GBR_check = any(series_raceinfo.str.contains('GBR'))
        GIH_check = any(series_raceinfo.str.contains('GIH'))
        GWD_check = any(series_raceinfo.str.contains('GWD'))
        IBS_check = any(series_raceinfo.str.contains('IBS'))
        ITU_check = any(series_raceinfo.str.contains('ITU'))
        JPT_check = any(series_raceinfo.str.contains('JPT'))
        KHV_check = any(series_raceinfo.str.contains('KHV'))
        LWK_check = any(series_raceinfo.str.contains('LWK'))
        MSL_check = any(series_raceinfo.str.contains('MSL'))
        MXL_check = any(series_raceinfo.str.contains('MXL'))
        PEL_check = any(series_raceinfo.str.contains('PEL'))
        PJL_check = any(series_raceinfo.str.contains('PJL'))
        PUR_check = any(series_raceinfo.str.contains('PUR'))
        STU_check = any(series_raceinfo.str.contains('STU'))
        TSI_check = any(series_raceinfo.str.contains('TSI'))
        YRI_check = any(series_raceinfo.str.contains('YRI'))

        checks = all([ACB_check, ASW_check,BEB_check,CDX_check,CEU_check,CHB_check,CHS_check,
                      CLM_check,ESN_check,FIN_check, GBR_check, GIH_check, GWD_check, IBS_check,
                      ITU_check, JPT_check, KHV_check, LWK_check, MSL_check, MXL_check,
                      PEL_check, PJL_check, PUR_check, STU_check])

        if checks == True:
            del_sequence = list(series_raceinfo[series_raceinfo.str.contains('ACB')])[0]
            all_races_common_sequence.append(del_sequence)

    return all_races_common_sequence

print(check_all_races(DHFR, DHFR_rowpairs), check_all_races(NQO2, NQO2_rowpairs), check_all_races(PSAT1, PSAT1_rowpairs))

## deletion phase for sequences common to all 26 races

fr_DHFR = open("ALL_DHFR.fa","r")
fr_NQO2 = open("ALL_NQO2.fa","r")
fr_PSAT1 = open("ALL_PSAT1.fa","r")
lines_DHFR = fr_DHFR.readlines()
lines_NQO2 = fr_NQO2.readlines()
lines_PSAT1 = fr_PSAT1.readlines()

import inspect
## purpose of this function is to find the name of a variable as a string
## this function is called in below function for writing filename
def retrieve_name(var):
        """
        Gets the name of var. Does it from the out most frame inner-wards.
        :param var: variable to get name from.
        :return: string
        """
        for fi in reversed(inspect.stack()):
            names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
            if len(names) > 0:
                return names[0]

def removing_commonseq(lines_arg, dataframe_arg, rowpairs_arg):
    lines_spec = [ x+y for x,y in zip(lines_arg[0::2], lines_arg[1::2]) ]

    spec_globalseq = check_all_races(dataframe_arg, rowpairs_arg)

    for line in lines_spec:
        for seq in spec_globalseq:
            if seq in line:
                lines_spec.remove(line)

    name = retrieve_name(lines_arg)

    fw = open("00%s.fa" % name[5:], 'w')
    ## the name of file writes to 00_DHFR.fa, 00_NQO2.fa, 00_PSAT1.fa
    lines_spec = ''.join(lines_spec)
    fw.write(lines_spec)
    print("success")

removing_commonseq(lines_DHFR, DHFR, DHFR_rowpairs)
removing_commonseq(lines_NQO2, NQO2, NQO2_rowpairs)
removing_commonseq(lines_PSAT1, PSAT1, PSAT1_rowpairs)
