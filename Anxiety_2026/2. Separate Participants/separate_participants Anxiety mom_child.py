 # -*- coding: utf-8 -*-
import os
import mne

# constants

parent_CHNL_PICK = ['Fp1S1E01','FzS1E02','F3S1E03','F7S1E04','C3S1E08','T7S1E09','PzS1E13','P3S1E14',
                    'P7S1E15','O1S1E16','O2S1E18','P4S1E19','P8S1E20','CzS1E24','C4S1E25','T8S1E26',
                    'F4S1E30','F8S1E31','Fp2S1E32']
child_CHNL_PICK = ['FP1S2E01','FzS2E02','F3S2E03','F7S2E07','C3S2E08','T7S2E09','PzS2E13','P3S2E14',
                    'P7S2E15','O1S2E16','O2S2E18','P4S2E19','P8S2E20','CzS2E24','C4S2E25','T8S2E26',
                    'F4S2E30','F8S2E31','FP2S2E32','Ref2']
parent_CHNL_RENAME = {
    'Fp1S1E01':'Fp1', 'FzS1E02':'Fz', 'F3S1E03': 'F3', 'F7S1E04': 'F7', 'C3S1E08':'C3', 'T7S1E09':'T7',
                     'PzS1E13':'Pz', 'P3S1E14': 'P3', 'P7S1E15':'P7', 'O1S1E16':'O1', 'O2S1E18':'O2', 'P4S1E19': 'P4',
                      'P8S1E20':'P8', 'CzS1E24':'Cz', 'C4S1E25':'C4', 'T8S1E26':'T8', 'F4S1E30':'F4', 'F8S1E31':'F8', 'Fp2S1E32':'Fp2'}
child_CHNL_RENAME = {
    'FP1S2E01':'Fp1', 'FzS2E02':'Fz', 'F3S2E03': 'F3', 'F7S2E07': 'F7', 'C3S2E08':'C3', 'T7S2E09':'T7', 'Ref2':'FCz',
                     'PzS2E13':'Pz', 'P3S2E14': 'P3', 'P7S2E15':'P7', 'O1S2E16':'O1','O2S2E18':'O2','P4S2E19': 'P4',
                      'P8S2E20':'P8', 'CzS2E24':'Cz', 'C4S2E25':'C4', 'T8S2E26':'T8', 'F4S2E30':'F4', 'F8S2E31':'F8', 'FP2S2E32':'Fp2'}


MONTAGE = mne.channels.make_standard_montage('standard_1020')



#def main(in_path, out_path): 
def separate_channels(in_path, out_path):
    """
    Separates 64 electrode (2 sets of 32) raw data into 2 separate
    data sets, renames channels, applies montage and re-references.
    The script reads all fif files from specified source folder and outputs
    the results into a specified output folder.
    :param in_path: path to source files (RAW) directory
    :param out_path: path to output files (EpochsArray) directory
    :return:
    """
    # loop over all input files
    print(os.listdir())
    os.chdir(in_path)
    for file in os.listdir():
        
        # only process .fif files
        if not file.endswith('.fif'):
            continue
        
        raw = mne.io.read_raw_fif(file, preload=True)
        
        # processing parent
        parent = raw.copy()
        parent.set_channel_types(dict(
                    {'Fp1S1E01':'eeg', 'FzS1E02':'eeg', 'F3S1E03': 'eeg', 'F7S1E04': 'eeg', 'C3S1E08':'eeg', 'T7S1E09':'eeg',
                     'PzS1E13':'eeg', 'P3S1E14': 'eeg', 'P7S1E15':'eeg', 'O1S1E16':'eeg', 'O2S2E18':'eeg', 'P4S1E19': 'eeg',
                      'P8S1E20':'eeg', 'CzS1E24':'eeg', 'C4S1E25':'eeg', 'T8S1E26':'eeg', 'F4S1E30':'eeg', 'F8S1E31':'eeg', 'Fp2S1E32':'eeg'}))
        parent.pick_channels(ch_names=parent_CHNL_PICK)
        parent.rename_channels(parent_CHNL_RENAME)
        parent.set_montage(MONTAGE)
        parent.filter(1, 50, method='iir')
        
        # processing child
        child = raw
        child.set_channel_types(dict(
                    {'FP1S2E01':'eeg', 'FzS2E02':'eeg', 'F3S2E03': 'eeg', 'F7S2E07': 'eeg', 'C3S2E08':'eeg', 'T7S2E09':'eeg',
                     'PzS2E13':'eeg', 'P3S2E14': 'eeg', 'P7S2E15':'eeg', 'O1S2E16':'eeg', 'O2S2E18':'eeg', 'P4S2E19': 'eeg',
                      'P8S2E20':'eeg', 'CzS2E24':'eeg', 'C4S2E25':'eeg', 'T8S2E26':'eeg', 'F4S2E30':'eeg', 'F8S2E31':'eeg', 'FP2S2E32':'eeg', 'Ref2':'eeg'}))
        child.pick_channels(ch_names=child_CHNL_PICK)
        child.rename_channels(child_CHNL_RENAME)
        child.set_montage(MONTAGE)
        child.filter(1, 50, method='iir')
        # parent's channels are using a not recording reference
        # channel by default, for child we need to manually reference
        # to the reference channel FCz, and then remove it.
        child, _ = mne.set_eeg_reference(child, ['FCz'])
        child.info['bads'] = ['FCz']
        child.pick_types(eeg=True, exclude='bads')
        
        # save processed subjects
        os.chdir(os.path.dirname(__file__))
        os.chdir(out_path)
        parent.save(file[:-7]+'mother_raw.fif')
        child.save(file[:-7]+'child_raw.fif')
        os.chdir(os.path.dirname(__file__))
        os.chdir(in_path)
if __name__ == "__main__":
    IN_PATH = 'D:/Anxiety_exp/1. Interactions_cut/control/FI_mom/'
    OUT_PATH = 'D:/Anxiety_exp/2. Interactions_seperated/control/'
    #main(IN_PATH, OUT_PATH)
    separate_channels(IN_PATH, OUT_PATH)
