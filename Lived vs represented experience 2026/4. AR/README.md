# 4. AR
- `AR.py`: Script for performing AR on the data. 
This script processes the epochs files in .fif format and applies auto-reject with a chosen parameters [ (1, 4, 8, 16 channels) for interpolation and Bayesian optimization for thresholding]. 
The cleaned epochs are saved as .fif files with '_AR_epo.fif' suffix.