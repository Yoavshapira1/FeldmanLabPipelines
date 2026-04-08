# FeldmanLabPipeline

The pipeline is divided into several phases, each handling a specific step in the data processing workflow.

## Folder Structure


### Pre processing:
- **1st phase - cut interactions/**: Scripts for cutting EEG files interactions based on external infromation about the triggers.
- **2nd phase - seperate/**: Scripts for separating mother and child electrodes.
- **3rd phase - to epochs/**: Scripts for converting raw data to epochs.
- **4. AR/**: Scripts for autoreject performing.
- **5. ICA/**: Scripts for ICA processing, including making ICA, checking properties, saving figures, and cleaning components.

### Connectivity analysis:
- **6. connectivity/**: Scripts for computing connectivity measures from clean epochs. Including 2 utilities scripts and a script for the connectivity computatiopn.
- **7. create surrogate data/**: Scripts for creating surrogate connectivity data. Including 3 utilities and 1 computation script. 
- **other scripts for analysis and visualization/**: Additional scripts for analysis and plots.