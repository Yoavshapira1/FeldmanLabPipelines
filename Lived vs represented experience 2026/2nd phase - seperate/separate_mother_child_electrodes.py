# -*- coding: utf-8 -*-
import os
import mne

# constants
child_CHNL_PICK = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
                      '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
                      '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32']
mom_CHNL_PICK = ['33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43',
                      '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54',
                      '55', '56', '57', '58', '59', '60', '61', '62', '63', '64']

child_chanel_rename = {
    '1': 'Fp1', '2': 'Fp2', '3': 'F3', '4': 'F4', '5': 'C3',
                        '6': 'C4', '7': 'P3', '8': 'P4', '9': 'O1', '10': 'O2',
                        '11': 'F7', '12': 'F8', '13': 'T7', '14': 'T8', '15': 'P7',
                        '16': 'P8', '17': 'Fz', '18': 'Cz', '19': 'Pz', '20': 'eog',
                        '21': 'FC1', '22': 'FC2', '23': 'CP1', '24': 'CP2', '25': 'FC5',
                        '26': 'FC6', '27': 'CP5', '28': 'CP6', '29': 'FT9', '30': 'FT10',
                        '31': 'TP9', '32': 'TP10'}
mom_chanel_rename = {
        '33': 'Fp1', '34': 'Fp2', '35': 'F3', '36': 'F4', '37': 'C3', '38': 'C4', '39': 'P3',
                        '40': 'P4', '41': 'O1', '42': 'O2', '43': 'F7', '44': 'F8', '45': 'T7', '46': 'T8',
                        '47': 'P7', '48': 'P8', '49': 'Fz', '50': 'Cz', '51': 'Pz', 
                        '52': 'eog','53': 'FC1','54': 'FC2', '55': 'CP1', '56': 'CP2',
                        '57': 'FC5', '58': 'FC6', '59': 'CP5',
                        '60': 'CP6', '61': 'FT9', '62': 'FT10', '63': 'TP9', '64': 'TP10'}

MONTAGE = mne.channels.make_standard_montage('standard_1020')


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
        
        # processing child
        child = raw.copy()
        child.pick_channels(ch_names=child_CHNL_PICK)
        child.set_channel_types({'20': 'eog'})
        child.rename_channels(child_chanel_rename)
        print(child.info['ch_names'])
        child.set_montage(MONTAGE, on_missing = 'warn')
        child.filter(1, 50, method='fir')
        
        # processing mom
        mom = raw
        mom.pick_channels(ch_names=mom_CHNL_PICK)
        mom.set_channel_types({'52': 'eog'})
        mom.rename_channels(mom_chanel_rename)
        mom.set_montage(MONTAGE, on_missing = 'warn')
        mom.filter(1, 50, method='fir')
        mom.plot_sensors(show_names = True)
        # creating an averagge reference, excluding the eye electrodes - 20 & 52.
        child, _ = mne.set_eeg_reference(child, ['Fp1', 'Fp2', 'F3', 'F4', 'C3','C4','P3', 'P4', 'O1', 'O2', 'F7',
                                                'F8', 'T7', 'T8', 'P7', 'P8', 'Fz', 'Cz', 'Pz', 'FC1', 'FC2',
                                                 'CP1', 'CP2', 'FC5',  'FC6',  'CP5', 'CP6', 'FT9',  'FT10', 'TP9', 'TP10'])
        mom, _ = mne.set_eeg_reference(mom, ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1',
                                             'O2', 'F7', 'F8','T7', 'T8', 'P7', 'P8', 'Fz', 'Cz', 'Pz',
                                              'FC1', 'FC2', 'CP1', 'CP2', 'FC5', 'FC6', 'CP5', 'CP6', 'FT9', 'FT10', 'TP9', 'TP10'])
        #mom.info['bads'] = ['FCz']
        #mom.pick_types(eeg=True, exclude='bads')
        
        # save processed subjects
        os.chdir(os.path.dirname(__file__))
        os.chdir(out_path)
        #child.save(file[:-4]+'_child_raw.fif')
        #mom.save(file[:-4]+'_mom_raw.fif')
        child.save(file[:-8]+'_child_raw.fif')
        mom.save(file[:-8]+'_mom_raw.fif')
        os.chdir(os.path.dirname(__file__))
        os.chdir(in_path)


if __name__ == "__main__":
    IN_PATH = 'source folder/'
    OUT_PATH = 'output folder/'
#    OUT_PATH = 'C:/Users/Linoy/Dropbox/post/to_epochs/Epochs_seperated/'
    separate_channels(IN_PATH, OUT_PATH)
