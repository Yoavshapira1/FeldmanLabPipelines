# -*- coding: utf-8 -*-
import mne
import os
import matplotlib.pyplot as plt


def save_figs(in_path, out_path):
    """
    saves plots of ica components of each subject
    :param in_path: path to source files (ICA components) directory
    :param out_path: path to output files (.png pictures) directory
    :return:
    """
    os.chdir(in_path)
    for file in os.listdir():
        if not file.endswith('.fif'):
            continue
        ica = mne.preprocessing.read_ica(file)
        ica.plot_components()
        #ica.plot_properties()  
       
        # save figure
        os.chdir(os.path.dirname(__file__))
        os.chdir(out_path)
        for i in plt.get_fignums():
            fig = plt.figure(i)
            name = file[:-4]+'_{}_plot.png'.format(i)
            fig.savefig(name)
        # set working dir back to input folder
        os.chdir(os.path.dirname(__file__))
        os.chdir(in_path)

        # close figure
        plt.close('all')

if __name__ == "__main__":
    IN_PATH =  'C:/Users/carme/Documents/Ruth Feldman LAB/anxiety experiment all/Linoys Analysis/5. ICA/clinical/Triade_without/'
    #'C:/Users/Linoy/Dropbox/post/to_epochs/ica_components/'
    OUT_PATH = 'C:/Users/carme/Documents/Ruth Feldman LAB/anxiety experiment all/Linoys Analysis/5.1 ICA figs/clinical/Triades/Triade_without/'
    #'C:/Users/Linoy/Dropbox/post/to_epochs/ICA_fig/'
    save_figs(IN_PATH, OUT_PATH)
