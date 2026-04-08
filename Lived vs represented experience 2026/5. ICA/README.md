# 5. ICA

## Files
- `first - make_ica.py`: Script to perform ICA on the data. 
This script reads epochs files in .fif format, fits an ICA model using the Infomax method, and saves the ICA components as .fif files with '_ica.fif' suffix.
- `second - save_ica_fig.py`: Script to save figures related to ICA. 
This script reads ICA component files, generates plots of the components, and saves them as PNG images to inspect later.
- `third - clean_ica_new.py`: Script to clean the data using ICA components.
This script uses predefined templates to identify bad ICA components (e.g., blinks) via correlation mapping, records bad component indices in a CSV file, and applies ICA cleaning by excluding the bad components from the epochs, saving the cleaned data as .fif files.