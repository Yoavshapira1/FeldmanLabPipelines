# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 11:08:28 2021

@author: Linoy
"""

import os
import mne
from mne.preprocessing.ica import corrmap

 
def clean_ica_comp(in_path_epochs, in_path_ica, out_path, templates):
    """
    Prompts user to select ica components and then applies them on
    EpochsArrays.
    :param in_path_epochs: path to source files (EpochsArray) directory
    :param in_path_ica: path to source files (ICA components) directory
    :param out_path: path to output files (EpochsArray) directory
    :param templates: list of tuples where first entry is name of file
    and second is index of ICA component
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
        corrmap(ica_ls, template=template, label='blinks', show=False, plot = False,
                threshold=.8)
        
    # load all EpochArrays from folder
    files_mne = sorted([file for file in os.listdir(in_path_epochs) if
                        file.endswith('fif')])
    os.chdir(in_path_epochs)
    epochs_ls = [mne.read_epochs(file, preload=True) for file in files_mne]

    # verify ica and epo files (mathicng subjects)
    for pair in zip(files_ica, files_mne):
        assert pair[0][:13] == pair[1][:13],\
            'unmatching pair- {}, {}'.format(pair[0], pair[1])

    # apply ica components and save subjects
    os.chdir(os.path.dirname(__file__))
    os.chdir(out_path)
    for x in zip(epochs_ls, ica_ls, sorted(os.listdir(in_path_epochs))):
        epochs = x[0]
        ica = x[1]
        name = x[2][:-4]+'_cleanICA_epo.fif'
        epochs_clean = ica.apply(epochs, exclude=ica.labels_['blinks'])
        epochs_clean.save(name)


if __name__ == "__main__":
    IN_PATH_EPOCHS = 'C:/Users/carme/Documents/Ruth Feldman LAB/anxiety experiment all/Linoys Analysis/4. AR/control/FI dad + conflicts/'
    IN_PATH_ICA = 'C:/Users/carme/Documents/Ruth Feldman LAB/anxiety experiment all/Linoys Analysis/5. ICA/control/FI_dad+conflicts/'
    OUT_PATH = 'C:/Users/carme/Documents/Ruth Feldman LAB/anxiety experiment all/Linoys Analysis/6.1 After ICA/control/FI_dad+conflicts/'
    TEMPLATES = [('Family_44_1FI_mom_mother_AR_ica.fif', 1),
                 ('Family_T43_FI_mom_child_AR_ica.fif', 1), 
                ('Family_T42_FI_mom_mother_AR_ica.fif', 2),
                ('Family_T110FI_mom_child_AR_ica.fif', 1)]
                
    clean_ica_comp(IN_PATH_EPOCHS, IN_PATH_ICA, OUT_PATH, TEMPLATES)
    
    # ('IV4641_080_Rest_child_ica.fif', 18)
    

