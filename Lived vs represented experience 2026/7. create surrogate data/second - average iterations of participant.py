# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:30:37 2023

goes over all the CSV files of surrogate data in a folder
arranges them by subject, and averages the connectivity values of all possible surrogates of that participant to a single surrogate  
output is csv files with the same number of participants as in the regular connectivity analysis
"""

import os
import pandas as pd

# Path to directory containing CSV files
directory = 'folder with all the possible combinations of surrogate data/'

files = [file for file in os.listdir(directory) if file.endswith('.csv')]

# Initialize a dictionary to store the grouped data
grouped_data = {}

# Iterate over each CSV file
for file in files:
    # Read the CSV file
    file_path = os.path.join(directory, file)
    df = pd.read_csv(file_path)
    
    # Create a new column named "pairs" by combining two columns
    df['pairs'] = df['channel_1'] + df['channel_2']
    
    # Sort the data based on the values of "channel_1" and "channel_2"
    df.sort_values(['channel_1', 'channel_2'], inplace=True)
    
    # Extract the first 10 characters from the file name
    file_prefix = file[:11]
    
    # Group the data by the first 10 characters and sum the values across files in specific columns based on the rows from "channel_1" and "channel_2" columns
    if file_prefix not in grouped_data:
        grouped_data[file_prefix] = df.groupby(['channel_1', 'channel_2'])[['alpha', 'beta']].sum()
    else:
        grouped_data[file_prefix] += df.groupby(['channel_1', 'channel_2'])[['alpha', 'beta']].sum()
    
# Print and save the results
for prefix, grouped_df in grouped_data.items():
    print(f"First 10 Characters: {prefix}")
    
    """
    # Divide the summed values by the number of files
    grouped_df /= len(grouped_data)
    print(len(grouped_data))
    """

    # Divide the summed values by the number of files with the same prefix
    num_files = len([file for file in files if file.startswith(prefix)])
    grouped_df /= num_files
    print(num_files)


    
    # Reset the index to convert grouped columns to regular columns
    grouped_df = grouped_df.reset_index()
    
    # Select specific columns for the output DataFrame
    output_columns = ['channel_1', 'channel_2', 'alpha', 'beta']
    grouped_df = grouped_df[output_columns]
    
    #print(grouped_df)
    #print()
    
    # Save the results as a CSV file in the original folder
    file_name = prefix + "_shuffle.csv"
    save_path = os.path.join(directory, file_name)
    grouped_df.to_csv(save_path, index=False)
    

