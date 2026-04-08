# 6. Connectivity

## Files
- `first - minimum_times_after_ICA.py`: *(Utility script)* Script to determine the number of epochs in each interaction for each subject, and outputs a CSV file with epoch counts per interaction, which is used for connectivity analysis.
- `second - connectivity 240 lenght of interaction 4f2f fourier.py`: *(Computational script)* Script for connectivity analysis. This script reads clean epochs files after AR, uses the CSV to select amount of epochs, computes spectral connectivity between child and mother channels using Fourier transform, and saves the connectivity matrices as CSV files.
- `third - concat_files with pandas.py`: *(Utility script)* Script to concatenate files for easier analysis. This script combines multiple CSV files and outputs a single pivoted CSV file with connectivity values organized by subject and electrode pairs.