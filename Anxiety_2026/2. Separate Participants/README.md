# 2nd Phase - Separate
- `separate_participants Anxiety <parent>_child.py`: Script to separate electrodes corresponding to parent and child. 
This script processes raw EEG data files in .fif format (from previous stage), separating the electrodes into two sets - parent (either mother or father accordingly to the script and given paths) and child. 
It applies the standard 1020 montage, filters the data from 1 to 50 Hz, and re-references to an average reference. 
The processed data for child and mother are saved as separate raw .fif files with '_child_raw.fif' and '_<parnet>_raw.fif' suffixes.