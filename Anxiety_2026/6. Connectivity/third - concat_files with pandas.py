import os
import glob
import pandas as pd
import re

# Set working directory
os.chdir('path to connectivity folder/')

# Get all CSV filenames in the directory
extension = 'csv'
all_filenames = [i for i in glob.glob(f'*.{extension}')]

# Define a regex pattern to extract subject IDs
pattern = r"(Family_[BT]\d+_{1,2}Family_[BT]\d+)_"

# Process each file
for file in all_filenames:
    match = re.search(pattern, file)
    if match:
        subject_id = match.group(1)  # Extract matched part
        print(f"Extracted subject ID: {subject_id}")
    else:
        print(f"Could not extract subject ID from {file}")

# Combine all CSV files into one DataFrame
combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])

# Ensure channel_1 and channel_2 are strings before concatenation
combined_csv["channel_1"] = combined_csv["channel_1"].astype(str)
combined_csv["channel_2"] = combined_csv["channel_2"].astype(str)
combined_csv["both"] = combined_csv["channel_1"] + "+" + combined_csv["channel_2"]

# Define within/between relationship
combined_csv["within/between"] = combined_csv.apply(
    lambda x: 'within_child' if 'child' in x['channel_1'] and 'child' in x['channel_2'] else 
              'within_mother' if 'mother' in x['channel_1'] and 'mother' in x['channel_2'] else 
              'between', axis=1)

# Filter only "between" relationships
filter_combined = combined_csv[combined_csv["within/between"].str.contains("between")]

# Reshape the DataFrame
df_melted = filter_combined.melt(id_vars=['subject_ID', 'both'], 
                    value_vars=['theta','alpha', 'beta'], 
                    var_name='value_type', 
                    value_name='value')

# Combine `both` and `value_type` into a single column
df_melted['both'] = df_melted['both'] + '_' + df_melted['value_type']

# Create a pivot table
combined_pivot = df_melted.pivot_table(
    index='subject_ID',
    columns='both',  
    values='value', 
    aggfunc='sum'  
)

# Convert pivot table to DataFrame and save
combined_pivot = pd.DataFrame(combined_pivot)
combined_pivot.to_csv("combined_csv.csv", encoding='utf-8-sig')

print(combined_pivot)
