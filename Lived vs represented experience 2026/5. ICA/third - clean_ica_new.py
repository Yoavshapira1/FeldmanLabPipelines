# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 13:05:48 2021

@author: yaara.shapira
"""

import os
import mne
from mne.preprocessing.ica import corrmap
import pandas as pd
import matplotlib.pyplot as plt

 
def clean_ica_comp(in_path_epochs, in_path_ica, out_path, templates, path_csv,
                   out_path_bads_include):
    """
    Prompts user to select ica components and then applies them on
    EpochsArrays.
    :param in_path_epochs: path to source files (EpochsArray) directory
    :param in_path_ica: path to source files (ICA components) directory
    :param out_path: path to output files (EpochsArray) directory
    :param templates: list of tuples where first entry is name of file
    and second is index of ICA component
    :param path_csv: path to output csv file, the csv file stores "bad"
    components indices for each subject
    :param out_path_bads_include: path for output files where the included ica
    components are the bad components
    :return:
    """

    # load ica components
    files_ica = sorted([file for file in os.listdir(in_path_ica) if
                        file.endswith('.fif')])
    os.chdir(in_path_ica)
    ica_ls = [mne.preprocessing.read_ica(file) for file in files_ica]

    # switch file names for indices in templates
    templates = [(files_ica.index(temp[0]), temp[1]) for temp in templates]

    # correlate ica objects with selected templates
    for template in templates:
        corrmap(ica_ls, template=template, label='blinks', show=False,
                threshold=.8)

    # write to output csv the bad components
    out_dict = {'Subject': [], 'bad components indices': []}
    for ica, name in zip(ica_ls, files_ica):
        out_dict['Subject'].append(name)
        out_dict['bad components indices'].append(
            [', '.join(map(str, ica.labels_['blinks']))])
    df = pd.DataFrame(out_dict)
    df.to_csv(path_csv, index=False)

    # load all EpochArrays from folder
    files_mne = sorted([file for file in os.listdir(in_path_epochs) if
                        file.endswith('fif')])
    os.chdir(in_path_epochs)
    epochs_ls = [mne.read_epochs(file, preload=True) for file in files_mne]

    # verify ica and epo files (matching subjects)
    for pair in zip(files_ica, files_mne):
        assert pair[0][:13] == pair[1][:13],\
            'unmatching pair- {}, {}'.format(pair[0], pair[1])

    # apply ica components and save subjects
    os.chdir(os.path.dirname(__file__))
    os.chdir(out_path)
    for x in zip(epochs_ls, ica_ls, sorted(os.listdir(in_path_epochs))):
        epochs = x[0].copy()
        ica = x[1]
        name = x[2][:-4]+'_cleanICA_epo.fif'
        epochs_clean = ica.apply(epochs, exclude=ica.labels_['blinks'])
        epochs_clean.save(name)
        

    # apply bad ica components and save subjects
    os.chdir(os.path.dirname(__file__))
    os.chdir(out_path_bads_include)
    for x in zip(epochs_ls, ica_ls, sorted(os.listdir(in_path_epochs))):
        epochs = x[0].copy()
        ica = x[1]
        name = x[2][:-4] + '_cleanICA_epo.fif'
        epochs_clean = ica.apply(epochs, include=ica.labels_['blinks'])
        epochs_clean.save(name)

if __name__ == "__main__":
    
    IN_PATH_EPOCHS = 'folder with EEG data after AR/'
    IN_PATH_ICA = 'folder with ICA components'
    OUT_PATH = 'output folder/'

    OUT_PATH_BADS_INCLUDE = 'folder for excluded ICA data/' #data files
    PATH_CSV = 'folder for excluded ICA data/' #list of bad ICA 
  
    #TEMPLATES final  = [("ZW1003Feedingraw_mother_AR_icaFeed.fif", 8),("ZW1005Feedingraw_mother_AR_icaFeed.fif", 0),("ZW1023Feedingraw_infant_AR_icaFeed.fif", 0),("ZW1011Feedingraw_mother_AR_icaFeed.fif", 7),("ZW1007Feedingraw_infant_AR_icaFeed.fif", 0), ("ZW1024Feedingraw_infant_AR_icaFeed.fif", 8),("ZW1019Feedingraw_mother_AR_icaFeed.fif", 4),("ZW1055Feedingraw_mother_AR_icaFeed.fif", 4),("ZW1068Feedingraw_mother_AR_icaFeed.fif", 8)]
   # TEMPLATES = [("FI02Fbaseline_father_epo_AR_ica.fif", 0),("FI02Fbaseline_infant_epo_AR_ica.fif", 4),("FI02SBlank_father_epo_AR_ica.fif", 2),("FI03Fbaseline_infant_epo_AR_ica.fif", 1), ("FI05SBO_infant_epo_AR_ica.fif", 9),("FI56FfreeInteraction_father_epo_AR_ica.fif", 0),("FI56FfreeInteraction_father_epo_AR_ica.fif", 4)]
   
    TEMPLATES = [("IV4611_048__Video_child_Czref_AR_ica.fif", 2),#red blue
                 ("IV4628_067__movie_mom_Czref_AR_ica.fif", 1)] #blue eyes
    #the templates must be in both the EEG epochs folder and the ICA components folder

    clean_ica_comp(IN_PATH_EPOCHS, IN_PATH_ICA, OUT_PATH, TEMPLATES, PATH_CSV,
                   OUT_PATH_BADS_INCLUDE)