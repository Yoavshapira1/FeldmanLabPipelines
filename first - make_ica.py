# -*- coding: utf-8 -*-
import os
import mne
from mne.preprocessing import ICA


def make_ica_comp(in_path, out_path):
    """
    Reads EpochsArray, finds ICA components and saves them in a file
    :param in_path: path to source files (EpochsArray) directory
    :param out_path: path to output files (ICA components) directory
    :return:
    """
    os.chdir(in_path)
    for file in os.listdir():
        if not file.endswith('.fif'):
            continue
        epochs = mne.read_epochs(file, preload=True)
        
        #epochs.plot(title = file)

        #epochs = mne.io.read_raw_fif(file, preload=True)
        ica = ICA(n_components=15, method='fastica', random_state=42)
        ica = ica.fit(epochs)
    
        # save ica components
        os.chdir(os.path.dirname(__file__))
        os.chdir(out_path)
        f_name = file[:-8]+'_ica.fif'
        ica.save(f_name)
        os.chdir(os.path.dirname(__file__))
        os.chdir(in_path)

if __name__ == "__main__":
    IN_PATH = 'C:/Users/carme/Documents/Ruth Feldman LAB/anxiety experiment all/Linoys Analysis/4. AR/control/FI dad + conflicts/'
    #'C:/Users/Linoy/Dropbox/post/to_epochs/Epochs_AR/'
    OUT_PATH = 'C:/Users/carme/Documents/Ruth Feldman LAB/anxiety experiment all/Linoys Analysis/5. ICA/control/FI dad + conflicts/'
    #'C:/Users/Linoy/Dropbox/post/to_epochs/ica_components/'
    make_ica_comp(IN_PATH, OUT_PATH)
