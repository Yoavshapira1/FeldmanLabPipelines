# -*- coding: utf-8 -*-

"""Created on Mon Jan  4 16:43:09 2021

@author: Linoy
"""
import mne
import pandas as pd
import os
import re


#calculates the number of epochs in each interaction 
#output - csv file with the numbers of epochs in each interaction - from which we create a table, from which the number of epochs will be used to measure IB connectivity

######### USER CONFIGURATION #################
'''
EXPECTED FOLDER STRUCTURE:
src_folder
    |- paradigm_folder_1
        |- subject1.fif
        |- subject2.fif
        .
        .
        .
    |- paradigm_folder_2
    .
    .
    .
'''
SRC_FOLDER_PATH = 'source folder/'
DEST_FOLDER_PATH = 'output folder/'  # output directory for csv folder


######## HELPER FUNCTIONS ####################
def extract_subj_code(name: str):
    pattern = '[0-9]_([0-9][0-9][0-9])'
    match = re.search(pattern, name)
    print("lala",name,match)
    return match.group(1)


######## MAIN SCRIPT #########################
# prepare dataframe to fill with values
df = pd.DataFrame(columns=['id', 'length', 'interaction', 'subject_ID'])

# look for subdirectories in source folder
os.chdir(SRC_FOLDER_PATH)
files = os.listdir()
files = [file for file in files if os.path.isdir(file)]

# for every paradigm directory
for paradigm in files:
    os.chdir(SRC_FOLDER_PATH)
    os.chdir(paradigm)
    src_files = os.listdir()
    src_files = [src for src in src_files if src.endswith('.fif')]
    # for every epochs file in current paradigm directory
    for src in src_files:
        epochs = mne.read_epochs(src, preload=True)
        entry = {
            'id':extract_subj_code(src),
            'length': len(epochs.drop_log),
            'interaction': paradigm,
            'subject_ID' : src[0:11],
        }
        df = df.append(entry, ignore_index=True)

# sort and save dataframe
df = df.sort_values(by=['length'])
df.to_csv(os.path.join(DEST_FOLDER_PATH, 'paradigm_len.csv'), index=False)