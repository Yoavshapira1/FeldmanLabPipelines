  # -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 15:22:45 2021

@author: Linoy
"""

#goes over all csv files with connectivity values and arranges them based on subject name (first column) frequency and electrode pair 

import os
import glob
import pandas as pd
os.chdir('folder with CSV connectivity files - minus the log file/')

extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
#combine all files in the list
combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
combined_csv["both"] = combined_csv["channel_1"] + "+"+combined_csv["channel_2"]
combined_csv["within/between"] = combined_csv.apply(lambda x: 'within_child' if 'child' in x['channel_1'] and 'child' in x['channel_1'] else 
    'within_mom' if 'mom' in x['channel_1'] and 'mom' in x['channel_2'] else 
    'between', axis=1)  
filter_combined = combined_csv[combined_csv["within/between"].str.contains("between")]

df_melted = filter_combined.melt(id_vars=['subject_ID', 'both'], 
                    value_vars=[ 'alpha', 'beta'], 
                    var_name='value_type', 
                    value_name='value')
print(df_melted.head())
# Concatenate `both` and `value_type` to create a new column that combines these
df_melted['both'] = df_melted['both'] + '_' + df_melted['value_type']
combined_pivot = df_melted.pivot_table(
    index='subject_ID',
    columns='both',  # These are the combinations of channels and value types
    values='value', 
    aggfunc='sum'  # Summing the values as in your example
)
combined_pivot = pd.DataFrame(combined_pivot)
combined_pivot.to_csv("combined_data_with_subject_id.csv",  encoding='utf-8-sig')
print(combined_pivot)
