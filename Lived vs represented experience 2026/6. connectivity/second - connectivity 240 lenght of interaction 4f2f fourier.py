import os
import mne
import pandas as pd
import numpy as np
from mne.connectivity import spectral_connectivity as sc
import re

# =========== USER CONFIGURATION ==========
# paths
PATH_DIR_SRC ='source folder with epochs files'
PATH_DIR_DEST = 'output folder/'
PATH_DURATION_CSV = '.xlsx file with the number of epochs for each interaction - based on the results of the previous script'

#was just ica ver 4, not replication before

# duration dictionary
SBJ_COL_NAME = 'subject_ID'
DUR_COL_NAME = 'min'


# offset configuration
OFFSET_START = 2
OFFSET_END = 2 
# channels
CHANNELS_NAMES = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1',
                     'O2', 'F7', 'F8', 'T7', 'T8', 'P7', 'P8', 'Fz', 'Cz',
                     'Pz', 'FC1', 'FC2', 'CP1', 'CP2', 'FC5', 'FC6', 'CP5',
                     'CP6', 'FT9', 'FT10', 'TP9', 'TP10']
CHANNELS_NAMES = [x + '_child' for x in CHANNELS_NAMES] + [x + '_mom' for x in CHANNELS_NAMES]

# paradigm tag
TAG = 'face240'


# ============ HELPER FUNCTIONS =============
def name_to_key(name):
    """
    translate file name to a valid key for duration dictionary
    :return:
    """
    pattern = "(.*_[0-9][0-9][0-9])_"
    match_obj = re.search(pattern, name)
    if match_obj:
        return match_obj.group(1)
    else:
        raise ValueError('the translation has failed for the name: {}'.format(name))


def min_cut_dict() -> dict:
    """
    dict with subject names as keys, and their respective duration as values
    :return: dict object
    """
    if PATH_DURATION_CSV.endswith('.csv'):
        df = pd.read_csv(PATH_DURATION_CSV)
    else:
        df = pd.read_excel(PATH_DURATION_CSV)
    df[SBJ_COL_NAME] = df[SBJ_COL_NAME].map(name_to_key)
    return dict(zip(df[SBJ_COL_NAME], df[DUR_COL_NAME]))


def get_clean_count(drop_log):
    """
    get count of clean epochs
    :param drop_log: epochs array drop log
    :return:
    """
    return len([x for x in drop_log if not x])


def synch_drop_logs(subj_1, subj_2):
    """
    synchronize drop logs between the two subjects, modified in place
    :param subj_1: mne raw instance
    :param subj_2: mne raw instance
    :return:
    """
    log_1 = subj_1.drop_log
    log_2 = subj_2.drop_log
    clean_1 = [(a, b) for a, b in zip(log_1, log_2) if not a]
    ind_drop_1 = [i for ((a, b), i) in zip(clean_1, list(range(len(clean_1))))
                  if not a and b]
    clean_2 = [(a, b) for a, b in zip(log_2, log_1) if not a]
    ind_drop_2 = [i for ((a, b), i) in zip(clean_2, list(range(len(clean_2))))
                  if not a and b]
    subj_1.drop(ind_drop_1)
    subj_2.drop(ind_drop_2)


def apply_offset(subj, start, end, duration=None):
    """
    drop 'start' number of epochs from the beginning of the data and 'end' from
    the end
    :param subj: mne raw instacne
    :param start: # of epochs to crop from the start
    :param end:   # of epochs to crop from the end
    :param duration:
    :return:
    """
    log = subj.drop_log
    ind_drop_start = list(range(len([x for x in log[:start] if not x])))
    clean = [x for x in log[:int(duration-end)] if not x]
    clean_total = [x for x in log if not x]
    ind_drop_end = list(range(len(clean), len(clean_total)))
    subj.drop(ind_drop_start+ind_drop_end)

# -----------------------------------------------------------------------------
# MAIN SCRIPT
# ASSUMPTIONS:
#       - For every experiment there are pairs, the naming conventions should
#       be such that sorting the files in A-Z order will yield all pairs
#       adjacent
#       - Original data length is the same for the two members in each pair
# -----------------------------------------------------------------------------
# split files in source folder into pairs (by experiment)
files_ls = os.listdir(PATH_DIR_SRC)
files_ls = [file for file in files_ls if file.endswith('.fif')]
files_ls.sort()
files_ls = np.array(files_ls).reshape(int(len(files_ls)/2), 2)

# log clean epochs count
df_log = pd.DataFrame(columns=['subject', 'clean epochs', 'duration'])
duration_dict = min_cut_dict()

# loop over every subject pair
for (subj_1, subj_2) in files_ls:
    # load and pre-process data
    os.chdir(PATH_DIR_SRC)
    raw_1 = mne.read_epochs(subj_1, preload=True)
    raw_2 = mne.read_epochs(subj_2, preload=True)
    raw_1.pick_types(eeg=True,
                     exclude=[])
    raw_2.pick_types(eeg=True,
                     exclude=[])
    duration = duration_dict[name_to_key(subj_1)]
    apply_offset(raw_1, OFFSET_START, OFFSET_END, duration)
    synch_drop_logs(raw_1, raw_2)
    drop_comb = zip(raw_1.drop_log, raw_2.drop_log)

    # log total/clean epochs
    clean_count = get_clean_count(drop_log=raw_1.drop_log)
    log_data = {'subject': subj_1[0:10],
                'clean epochs': clean_count,
                'duration': duration}
    df_log = df_log.append(log_data, ignore_index=True)

    # preparations for spectral connectivity
    data_1 = raw_1.get_data()
    data_2 = raw_2.get_data()
    data_combined = np.concatenate((data_1, data_2), axis=1)
    info = mne.create_info(
        ch_names=CHANNELS_NAMES,
        ch_types=np.repeat('eeg', 62), sfreq=raw_1.info['sfreq'])
    events = np.array([np.array([i, 0, i])
                       for i in range(data_combined.shape[0])])
    events_id = dict(zip([str(x[0]) for x in events], [x[0] for x in events]))
    raw_combined = mne.EpochsArray(data_combined, info, events, -0.5,
                                   events_id)
    raw_combined.info['chs'] = raw_1.info['chs']+raw_2.info['chs']
    freq_bands = {'alpha': (7, 13), 
                  'beta': (13.5, 29.5)}
    fmin = np.array([f for f, _ in freq_bands.values()])
    fmax = np.array([f for _, f in freq_bands.values()])

    # spectral connectivity
    sc_data = sc(raw_combined, method='wpli', fmin=fmin, fmax=fmax,
                 mode='fourier', faverage=True, n_jobs=1, verbose=False)
    connB, freqsB, timesB, n_epochsB, n_tapersB = sc_data

    # export as .csv file
    os.chdir(PATH_DIR_DEST)
    file_name = subj_1[0:11]+TAG+'.csv'
    chnl_1 = np.array(list(range(62)) * 62)
    chnl_2 = chnl_1.copy()
    chnl_1.sort()
    df =\
    pd.DataFrame(
        dict(channel_1=chnl_1, channel_2=chnl_2, subject_ID = subj_1[0:11],
             **{key: np.reshape(connB[:, :, idx], 62 ** 2)
                for idx, key in enumerate(freq_bands.keys())})
            )
    df = df.loc[
        (df['beta'] > 0) | (df['alpha'] > 0)]

    channel_map = {key: val for key, val in enumerate(CHANNELS_NAMES)}
    df = df.replace({'channel_1': channel_map, 'channel_2': channel_map})
    df.to_csv(file_name)

os.chdir(PATH_DIR_DEST)
df_log.to_csv('clean epochs log ' + TAG + '.csv', index=False)