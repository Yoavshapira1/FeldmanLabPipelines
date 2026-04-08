# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 15:27:19 2021

@author: linoy.schwart
"""

import os
import mne
import numpy as np
from autoreject import AutoReject


def autoreject_clean(in_path, out_path):
    """
    Reads epochs array and cleans it with autoreject's AutoReject
    :param in_path: path to source files (EpochsArray) directory
    :param out_path: path to output files (EpochsArray) directory
    :return:
    """
    os.chdir(in_path)
    for file in os.listdir():
        epochs = mne.read_epochs(file)
        ar = AutoReject(n_interpolate=np.array([1, 4, 8, 16]), #was 1,2,4,8. i used 1,4,8,16
                        thresh_method='bayesian_optimization', random_state=42, verbose = False)
        epochs_clean = ar.fit_transform(epochs)
       
        # save EpochsArray
        os.chdir(os.path.dirname(__file__))
        os.chdir(out_path)
        name = file[:-8]+'_AR_epo.fif'
        epochs_clean.save(name)
        os.chdir(os.path.dirname(__file__))
        os.chdir(in_path)


if __name__ == "__main__":
    IN_PATH = 'source foler/'
    #'C:/Users/Linoy/Dropbox/post/to_epochs/Epochs_ready/'
    OUT_PATH = 'output folder/'
    #'C:/Users/Linoy/Dropbox/post/to_epochs/Epochs_AR/'
    autoreject_clean(IN_PATH, OUT_PATH)
