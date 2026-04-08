# -*- coding: utf-8 -*-
import mne
import pandas as pd
import re
import os


def extract_subj_code(name):
    pattern = r'_([0-9][0-9][0-9])_'
    m = re.search(pattern, name)
    return int(m.group(1))


def crop_subjects(csv_path, src_path, dest_path):
    # read csv file
    df = pd.read_csv(csv_path)

    # iterate over src files
    files = os.listdir(src_path)
    files = [file for file in files if file.endswith('.vhdr')]
    for file in files:
        os.chdir(src_path)
        subj_code = extract_subj_code(file)

        # check if .csv contains subject, if not skip
        if subj_code not in list(map(extract_subj_code, df['Subject'])):
            print('skipped {}'.format(subj_code))
            continue

        # read raw data
        raw = mne.io.read_raw_brainvision(file, preload=True)
        df_subj = df.loc[df['Subject'].map(extract_subj_code) == subj_code]
        intervals = zip(df_subj['Time MS_start'], df_subj['Time MS_end'],
                        df_subj['Interaction'], df_subj['Trigger'])

        # iterate over intervals
        os.chdir(dest_path)
        for start, stop, paradigm, trigger in intervals:
            cropped = raw.copy()
            cropped.crop(start/1000, stop/1000)

            # save file
            cropped.save('{}_{}_{}_raw.fif'.format(file[:-5], paradigm,
                                                   trigger), overwrite=True)




if __name__ == "__main__":
    CSV_PATH = 'table with start and end time of each interaction.csv'
    SRC_PATH = 'source folder with EEG files'
    DEST_PATH = 'output folder'
    crop_subjects(CSV_PATH, SRC_PATH, DEST_PATH)