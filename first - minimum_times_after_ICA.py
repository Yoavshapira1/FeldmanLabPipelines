# -*- coding: utf-8 -*-

"""Created on Mon Jan  4 16:43:09 2021

@author: Linoy
"""
import mne
import pandas as pd
import os
import re


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
SRC_FOLDER_PATH = 'D:/parenting/6.1 After ICA/control/mom_dad_analysis/'
DEST_FOLDER_PATH = 'D:/parenting/6.1 After ICA/control/mom_dad_analysis/'  # output directory


######## HELPER FUNCTIONS ####################
def extract_subj_code(name: str):
    id = name[0:11]
    print("your ID is", id)
    return id


######## MAIN SCRIPT #########################
# prepare dataframe to fill with values
df = pd.DataFrame(columns=['id', 'length', 'interaction'])

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
            'interaction': paradigm
        }
        df = df.append(entry, ignore_index=True)

# sort and save dataframe
df = df.sort_values(by=['length'])
df.to_csv(os.path.join(DEST_FOLDER_PATH, 'minimum_times_after_interactions.csv'), index=False)