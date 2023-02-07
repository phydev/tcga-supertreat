# TCGA data scraping

 Download gene expression data from TCGA for a subset of patients selected in the SuPerTreat project.

## How it works?
1 - Access [GDC data portal Repository](https://portal.gdc.cancer.gov/repository), filter the data of interest and download the list of entries by clicking on the button `JSON` (see figure bellow). This file will be your `manifest.json`.

2 - Provide a list of case ids such as `data/supertreat_cases.csv`.

3 - Run `src/main.py`.

The script will link files and case ids and then filter the entries in the manifest using the provided case ids. Then it downloads all the selected files from GDC and stores in `data/`.


