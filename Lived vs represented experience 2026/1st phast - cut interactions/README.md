# 1st Phase - Cut Interactions
`Cut_interactions_spesific_triggers.py`: Script to cut interactions using specific trigger points.
This script processes EEG data files in BrainVision format (.vhdr) and crops them into segments based on interaction intervals defined in a CSV file. 
The CSV contains columns for subject codes, start and end times (in milliseconds), interaction paradigms, and trigger types. 
For each subject, the script extracts the relevant intervals, crops the raw data accordingly, and saves the cropped segments as a raw .fif file with filename indicating the relevant information.