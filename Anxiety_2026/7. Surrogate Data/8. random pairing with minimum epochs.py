# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 10:36:03 2025

@author: linoy.schwart
"""

import os
import mne
import pandas as pd
import numpy as np
import itertools
import random
from mne.connectivity import spectral_connectivity as sc

# -----------------------------------------------------------------------------
# USER CONFIGURATIONS (SCRIPT CONSTANTS)
#   PATH_DIR_SRC : Path to source files folder
#   PATH_DIR_DEST: Path to target output folder
#   PATH_DURATION_CSV: Path to .csv file containing a duration column, the
#       duration is the minimal time between the different paradigms for each
#       subject. The duration
#   SBJ_COL_NAME : Name of subject names column
#   DUR_COL_NAME : Name of number of epochs column
#   OFFSET_START : Margin of epochs to crop from the beginning of the data
#   OFFSET_END   : Margin of epochs to crop from the end of the data (after
#   TAG          : Paradigm tag
#       cropping the by the duration value)
# -----------------------------------------------------------------------------
PATH_DIR_SRC = 'epochs after ICA/'
PATH_DIR_DEST = 'path to surrogated connectivity/'
PATH_DURATION_CSV = 'utility file.xlsx'     # the output from running ths file "first - minimum[...].py"

# duration dictionary
SBJ_COL_NAME = 'Subject_ID'
DUR_COL_NAME = 'min360' #could be minumum or face and then -110


# offset configuration
OFFSET_START = 2 #was 2
#changes between 2 for rest and 110 for face/ skype
OFFSET_END =  0 #was 0 for mothers control, 40 for mother control,70 for mother clinical, 45 dad clinical
#was just ica ver 4, not replication before

TAG = 'Shuffle FI_mom'

CHANNELS_NAMES = ['Fp1', 'Fz', 'F3', 'F7', 'C3', 'T7',
                  'Pz', 'P3', 'P7', 'O1', 'O2', 'P4',
                  'P8', 'Cz', 'C4', 'T8', 'F4', 'F8', 'Fp2']

CHANNELS_NAMES = [x + '_child' for x in CHANNELS_NAMES] + [x + '_mom' for x in CHANNELS_NAMES]

# -----------------------------------------------------------------------------
# USER ARGUMENTS VALIDATION
# -----------------------------------------------------------------------------
assert os.path.isdir(PATH_DIR_SRC), "invalid source folder"
assert os.path.isdir(PATH_DIR_DEST), "invalid destination folder"
assert os.path.isfile(PATH_DURATION_CSV), "invalid path to csv file"
assert PATH_DURATION_CSV.endswith(".xlsx"), "invalid file type"
excel_file = pd.read_excel(PATH_DURATION_CSV)
assert SBJ_COL_NAME in excel_file, \
    "csv file does not contain mandatory subject name column"
assert DUR_COL_NAME in excel_file, \
    "csv file does not contain mandatory duration column"
assert isinstance(OFFSET_START, int), "offset should be an integer value"
assert isinstance(OFFSET_END, int), "offset should be an integer value"


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def duplicate_condition_check(name1, name2) -> bool:
    if 'mother' in name1 and 'mother' in name2:
        return False
    if 'child' in name1 and 'child' in name2:
        return False
    if name1[1:11] == name2[1:11]:
        return False
    return True


def min_cut_dict() -> dict:
    """
    dict with subject names as keys, and their respective duration as values
    :return: dict object
    """
    excel_file = pd.read_excel(PATH_DURATION_CSV)
    return dict(zip(excel_file[SBJ_COL_NAME], excel_file[DUR_COL_NAME]))

def synch_drop_logs(subject_1, subject_2):
    """
    synchronize drop logs between the two subjects, modified in place
    :param subj_1: mne raw instance
    :param subj_2: mne raw instance
    :return:
    """
    log_1 = subject_1.drop_log
    log_2 = subject_2.drop_log

    # for cross subject synch with different epochs count
    ind_drop_1 = []
    ind_drop_2 = []
    if len(log_1) > len(log_2):
        clean_len = len([i for i in log_1[len(log_2):] if not i])
        ind_drop_1 = [i for i in range(len(subject_1.get_data())-clean_len,
                                       len(subject_1.get_data()))]
        log_1 = log_1[:len(log_2)]
    elif len(log_2) > len(log_1):
        clean_len = len([i for i in log_2[len(log_1):] if not i])
        ind_drop_2 = [i for i in range(len(subject_2.get_data())-clean_len,
                                       len(subject_2.get_data()))]
        log_2 = log_2[:len(log_1)]

    clean_1 = [(a, b) for a, b in zip(log_1, log_2) if not a]
    ind_drop_1 += [i for ((a, b), i) in zip(clean_1, list(range(len(clean_1))))
                   if not a and b]
    clean_2 = [(a, b) for a, b in zip(log_2, log_1) if not a]
    ind_drop_2 += [i for ((a, b), i) in zip(clean_2, list(range(len(clean_2))))
                   if not a and b]
    subject_1.drop(ind_drop_1)
    subject_2.drop(ind_drop_2)
    
def get_clean_count(drop_log):
    """
    get count of clean epochs
    :param drop_log: epochs array drop log
    :return:
    """
    return len([x for x in drop_log if not x])    


# -----------------------------------------------------------------------------
# MAIN SCRIPT
# ASSUMPTIONS:
#       - For every experiment there are pairs, the naming conventions should
#       be such that sorting the files in A-Z order will yield all pairs
#       adjacent
#       - Original data length is the same for the two members in each pair
# -----------------------------------------------------------------------------
# split files in source folder into pairs (by experiment)
file_ls = os.listdir(PATH_DIR_SRC)
file_ls = [file for file in file_ls if file.endswith('.fif')]
mother_ls = [file for file in file_ls if 'mother' in file]
infant_ls = [file for file in file_ls if 'child' in file]
file_ls = list(itertools.product(infant_ls, mother_ls))
file_ls = [file for file in file_ls if
           duplicate_condition_check(file[0], file[1])]
dic_duration = min_cut_dict()


# shuffle the list
#random.seed(42)
random.shuffle(file_ls)

# limit number of pairs
#file_ls = file_ls[:500]

# log clean epochs count
df_log = pd.DataFrame(columns=['subject1', 'subject2', 'clean epochs' ])
duration_dict = min_cut_dict()

# Initialize DataFrame for logging pair combinations and clean epochs
pair_clean_epochs_log = pd.DataFrame(columns=["Pair", "Total Clean Epochs"])

# loop over every subject pair
# loop over every subject pair
for (subj_1, subj_2) in file_ls:
    # Load and pre-process data
    os.chdir(PATH_DIR_SRC)
    raw_1 = mne.read_epochs(subj_1, preload=True)
    raw_2 = mne.read_epochs(subj_2, preload=True)
    raw_1.pick_types(eeg=True, exclude=[])
    raw_2.pick_types(eeg=True, exclude=[])

    # Synchronize drop logs
    synch_drop_logs(raw_1, raw_2)

    # Calculate clean epochs
    clean_count = get_clean_count(drop_log=raw_1.drop_log)
    log_data = {
        'subject_1': subj_1[:11],
        'subject_2': subj_2[:11],
        'clean epochs': clean_count
    }
    df_log = df_log.append(log_data, ignore_index=True)

    # Skip spectral connectivity if there are fewer than 110 clean epochs
    if clean_count < 40:
        print(f"Skipping pair {subj_1[:8]} and {subj_2[:8]}: insufficient clean epochs ({clean_count})")
        continue

    # Prepare for spectral connectivity
    data_1 = raw_1.get_data()
    data_2 = raw_2.get_data()
    data_combined = np.concatenate((data_1, data_2), axis=1)
    info = mne.create_info(
        ch_names=CHANNELS_NAMES,
        ch_types=np.repeat('eeg', 38),
        sfreq=raw_1.info['sfreq']
    )
    events = np.array([[i, 0, i] for i in range(data_combined.shape[0])])
    events_id = dict(zip([str(x[0]) for x in events], [x[0] for x in events]))
    raw_combined = mne.EpochsArray(data_combined, info, events, -0.5, events_id)
    raw_combined.info['chs'] = raw_1.info['chs'] + raw_2.info['chs']

    # Define frequency bands
    freq_bands = {
        'theta': (4, 7),
        'alpha': (7, 13),
        'beta': (13, 29),
        'gamma': (30, 48)
    }
    fmin = np.array([f[0] for f in freq_bands.values()])
    fmax = np.array([f[1] for f in freq_bands.values()])

    # Perform spectral connectivity analysis
    sc_data = sc(
        raw_combined,
        method='wpli',
        fmin=fmin,
        fmax=fmax,
        mode='fourier',
        faverage=True,
        n_jobs=1,
        verbose=False
    )
    connB, freqsB, timesB, n_epochsB, n_tapersB = sc_data

    # Export results as CSV
    os.chdir(PATH_DIR_DEST)
    file_name = f'{subj_1[:11]}_{subj_2[:11]}_{TAG}.csv'
    chnl_1 = np.array(list(range(38)) * 38)
    chnl_2 = chnl_1.copy()
    chnl_1.sort()
    df = pd.DataFrame(
        dict(
            channel_1=chnl_1,
            channel_2=chnl_2,
            subject_ID=subj_1[:11],
            subject_ID2=subj_2[:11],
            **{key: np.reshape(connB[:, :, idx], 38**2) for idx, key in enumerate(freq_bands.keys())}
        )
    )
    df = df.loc[(df['theta'] > 0) | (df['alpha'] > 0) | (df['beta'] > 0) | (df['gamma'] > 0)]
    channel_map = {key: val for key, val in enumerate(CHANNELS_NAMES)}
    df.replace({'channel_1': channel_map, 'channel_2': channel_map}, inplace=True)
    df.to_csv(file_name)

# Save log file
os.chdir(PATH_DIR_DEST)
df_log.to_csv(f'clean_epochs_log_{TAG}.csv', index=False)
