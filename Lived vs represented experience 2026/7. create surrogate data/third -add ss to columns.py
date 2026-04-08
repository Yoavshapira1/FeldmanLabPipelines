# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 14:40:58 2023

@author: linoy.schwart
"""

import os
import pandas as pd

#utility script - adds a column with participant ID

# Path to directory containing CSV files
directory = 'folder with surrogate data csv files/'

# Get list of CSV files in the directory
files = [file for file in os.listdir(directory) if file.endswith('.csv')]

# Iterate over each CSV file
for file in files:
    # Read the CSV file
    file_path = os.path.join(directory, file)
    df = pd.read_csv(file_path)
    
    # Extract the first 8 characters from the file name
    new_column = file[:11]
    
    # Add a new column with the first 8 characters of the file name
    df['subject_ID'] = new_column
    
    # Save the modified DataFrame as a new CSV file
    new_file_name = file.replace('.csv', '_with_names.csv')
    new_file_path = os.path.join(directory, new_file_name)
    df.to_csv(new_file_path, index=False)