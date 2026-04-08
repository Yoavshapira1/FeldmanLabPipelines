# 2nd Phase - Separate
- `separate_mother_child_electrodes.py`: Script to separate electrodes corresponding to mother and child. 
This script processes raw EEG data files in .fif format (from previous stage), separating the electrodes into two sets - mother and child. 
It applies the standard 1020 montage, filters the data from 1 to 50 Hz, and re-references to an average reference. 
The processed data for child and mother are saved as separate raw .fif files with '_child_raw.fif' and '_mom_raw.fif' suffixes.