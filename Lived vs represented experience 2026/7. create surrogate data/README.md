# 7. Create Surrogate Data

## Files
- `first - random pairing with minimum epochs over 120 fourier movie.py`: *(Computing script)* Script for pairing surrogated data with minimum common epochs. This script generates surrogate connectivity data by pairing participants from different dyads, computes spectral connectivity using Fourier transform, and saves the results as CSV files for each surrogate combination.
- `second - average iterations of participant.py`: *(Utilitiy script)* Script to average surrogated connectivity values for each participant. This script processes multiple CSV files of surrogate connectivity data, groups them by subject, averages the connectivity values across all surrogate iterations for each participant, and outputs consolidated CSV files.
- `third -add ss to columns.py`: *(Utilitiy script)* Script to add the subject name to columns. 
- `create final tables with ROI.py`: *(Utilitiy script)* Script to create tables with Regions of Interest (ROI). This script aggregates connectivity data into ROIs and outputs tables with connectivity values for each ROI.