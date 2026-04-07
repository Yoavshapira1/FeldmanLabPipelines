# -*- coding: utf-8 -*-
import mne
import os


def make_epochs(in_path, out_path):
    """
    Reads raw .fif files from specified path and outputs EpochsArray
    files to specified output path
    :param in_path: path to source files (RAW) directory
    :param out_path: path to output files (EpochsArray) directory
    :return:
    """
    os.chdir(in_path)
    for file in os.listdir():
        # only process .fif files
        if not file.endswith('.fif'):
            continue
        
        # like yaara did - 0.5 
        raw = mne.io.read_raw_fif(file, preload=True)
        events = mne.make_fixed_length_events(raw, duration=0.5)
        for i in range(events.shape[0]):
            events[i][2] = i
        epochs = mne.Epochs(raw, events, tmin=-0.5, tmax=0.5, preload=True)
        
        # save EpochsArray
        os.chdir(os.path.dirname(__file__))
        os.chdir(out_path)
        name = file[:-8]+'_epo.fif'
        epochs.save(name)
        os.chdir(os.path.dirname(__file__))
        os.chdir(in_path)


if __name__ == "__main__":
    IN_PATH = 'D:/Anxiety_exp/2.1 Interactions_seperated_fixed/'
    #'C:/Users/Linoy/Dropbox/post/to_epochs/Epochs_seperated/'
    OUT_PATH = 'D:/Anxiety_exp/3. Epochs/'

#    OUT_PATH = 'C:/Users/Linoy/Dropbox/post/to_epochs/Epochs_ready/'
    make_epochs(IN_PATH, OUT_PATH)
