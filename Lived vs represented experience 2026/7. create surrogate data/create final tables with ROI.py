# -*- coding: utf-8 -*-
"""
Created on Sun Nov 21 08:07:15 2021

@author: linoy.schwart
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 16:06:50 2021

@author: Linoy
"""

#creates tables with entire ROIs instead of single electrodes for analysis


from scipy.stats import ttest_ind, ttest_rel
from statistics import stdev, mean
import pandas as pd
import scipy.stats
import mne.stats


# #### HELPER FUNCTIONS ###
def concat_name(mom_chnl, child_chnl):
    return '{}_mom+{}_child'.format(mom_chnl, child_chnl)


def mix_groups(m_group, c_group):
    return [concat_name(i, j) for i in m_group for j in c_group]


# #### USER CONFIGURATION ####
PATH_IN_TABLE_1 = 'Excel file with data of the connectivity across all possible links in all participants.xlsx'
PATH_IN_TABLE_2 = 'Excel file with data of the connectivity across all possible links in all participants - surrogate data.xlsx' # mandatory rest is
# the second(2) path!
#PATH_IN_TABLE_3 = r'C:\Users\alexk\PycharmProjects\ttest_linoy_v05_09\skype_ver7code_dc_wpli.xlsx'
# another path

# path to output table with wilcoxon for each IB link
PATH_OUT_TABLE_TESTS = 'output with wilcoxon -FDR corrected for each ROI link.csv'
# list of different column combinations to p♦erform ttest on
PATH_OUT_TABLE_COLUMNS = 'table output with IB connectivity for each ROI link - data of real dyads and surrogate dyads.csv'


CHILD_GROUPS = [['T8','P8'], ['T7','P7'], ['F4','F8'], ['F3','F7']] 
MOTHER_GROUPS = [['T8','P8'], ['T7','P7'], ['F4','F8'], ['F3','F7']]

# lists of subjects to exclude
TABLE_1_EXCLUDE_LS = []
TABLE_2_EXCLUDE_LS = []


# standard deviation coefficient
COEF = 8

# type of test to perform, use "ttest_rel" for dependent test,
# use ttest_ind for independent test
ttest = ttest_rel

# #### MAIN SCRIPT PART ####
exclude_ls = list(set(TABLE_1_EXCLUDE_LS + TABLE_2_EXCLUDE_LS))

# convert input to column names
test_ls = [mix_groups(i, j) for i in MOTHER_GROUPS for j in CHILD_GROUPS]
#print(test_ls)

# load input table 1
if PATH_IN_TABLE_1.endswith('.csv'):
    in_table_1 = pd.read_csv(PATH_IN_TABLE_1)
else:
    in_table_1 = pd.read_excel(PATH_IN_TABLE_1)
# exclude subjects
in_table_1 = in_table_1.loc[~in_table_1['subject_ID'].isin(exclude_ls)]
#print(in_table_1)

# load input table 2
if PATH_IN_TABLE_2.endswith('.csv'):
    in_table_2 = pd.read_csv(PATH_IN_TABLE_2)
else:
    in_table_2 = pd.read_excel(PATH_IN_TABLE_2)
# exclude subjects
in_table_2 = in_table_2.loc[~in_table_2['subject_ID'].isin(exclude_ls)]

# exclude missing subjects, if you don't want to automatically exclude entries
# that are not in both tables change "if True" to "if False"
if True:
    set_1 = set(list(in_table_1['subject_ID']))
    set_2 = set(list(in_table_2['subject_ID']))
    exclude_from_1 = list(set_1 - set_2)
    in_table_1 = in_table_1.loc[~in_table_1['subject_ID'].isin(exclude_from_1)]
    exclude_from_2 = list(set_2 - set_1)
    in_table_2 = in_table_2.loc[~in_table_2['subject_ID'].isin(exclude_from_2)]

# prepare output DF for tests
df_out = pd.DataFrame(columns=['Test', 'P value', 'P value mult',
                               'mean group 1', 'stdev group 1',
                               'mean group 2', 'stdev group 2',
                               'subjects included'])

# prepare output DF for columns
subj_names_1 = pd.DataFrame({'subj list 1': in_table_1['subject_ID']})
print(subj_names_1)
subj_names_2 = pd.DataFrame({'subj list 2': in_table_2['subject_ID']})
df_out_cols = pd.concat([subj_names_1, subj_names_2], axis=1)

test_count = len(test_ls) 

# add different frequencies to the tests
freq_ls = ['_beta','_alpha']
#freq_ls = ['_alpha']
test_ls = [[[col + f for col in group] for group in test_ls] for f in freq_ls]
p_values = []
df_fdr = pd.DataFrame()
data = {}
for freq in test_ls:
    count = 0
    for test in freq:
        #print(in_table_1)
        count += 1
        values_1 = in_table_1[test]
        values_2 = in_table_2[test]

        # remove extra lines
        #values_1 = values_1[0:-1]
        #values_2 = values_2[0:-1]
        #print(values_1)

        # take mean of rows
        values_1 = values_1.mean(axis=1)
        values_2 = values_2.mean(axis=1)

        # names
        subj_names = in_table_1['subject_ID']

        # generate delta list
        delta_ls = [abs(a - b) for a, b in zip(values_1, values_2)]

        # compute stdev and mean for delta list
        delta_stdev = stdev(delta_ls)
        delta_mean = mean(delta_ls)

        # zip values, delta and names, remove unfitting entries
        good_entries = [(name, val_1, val_2) for name, val_1, val_2, val_d
                        in zip(subj_names, values_1, values_2, delta_ls)
                        if abs(delta_mean - val_d) <= delta_stdev * COEF]

        # generate used subjects name list, update value lists
        included_ls = [x[0] for x in good_entries]
        values_1 = [x[1] for x in good_entries]
        values_2 = [x[2] for x in good_entries]

        # before overriding the original values copy the list
        notDelta_names = set(list(subj_names)) - set(included_ls)

        # perform test
        # _, p_val = ttest(values_1, values_2)
        _, p_val = scipy.stats.wilcoxon(values_1, values_2, "wilcox", False)
        p_values.append(p_val)
        data = {
            'Test': test,
            'P value': p_val,
            'mean group 1': mean(values_1),
            'stdev group 1': stdev(values_1),
            'mean group 2': mean(values_2),
            'stdev group 2': stdev(values_2),
            'subjects included': included_ls,
            'subject subtracted': notDelta_names,
            'frequency': freq[0][0][-8::],
            'delta between mean1 and mean2': (mean(values_1) - mean(values_2))
        }
        df_out = df_out.append(data, ignore_index=True)
        df_out_cols = pd.concat([df_out_cols,
                                 pd.DataFrame({str(test): values_1}),
                                 pd.DataFrame({str(test): values_2})],
                                axis=1)

    _, corrected = mne.stats.fdr_correction(p_values)
    data2 = {}
    p_values = []
    for fdr_fixed in corrected:
        data2 = {
            'FDR_FIXED': fdr_fixed
        }
        df_fdr = df_fdr.append(data2, ignore_index =True)


df_out = pd.concat([df_out,df_fdr], axis=1)

# save output DF as .csv
df_out.to_csv(PATH_OUT_TABLE_TESTS, index=False)
df_out_cols.to_csv(PATH_OUT_TABLE_COLUMNS, index=False)