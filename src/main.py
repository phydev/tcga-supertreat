# download TCGA data from GDC using the GDC API
# https://docs.gdc.cancer.gov/API/Users_Guide/Getting_Started/
# we have a manifest file with all the file names and UUIDs
# we have a list of case UUIDs for the supertreat cases
# we need to download the file info for each case and link the file UUID to the case UUID
# then we need to download the files keeping the original file names

import pandas as pd
import requests
import json
import io

manifest_file = '../data/manifest.json'

# open manifest file with file names and UUIDs
with open(manifest_file) as file:

    # load json file as a dictionary
    manifest = json.load(file)

# create a dictionary with file UUIDs as keys and file names as values
file_dict = {}

for file in manifest:
    file_dict[file["cases"][0]["case_id"]] = file['file_name']

# load TGCA harmonized clinical data
clin = pd.read_csv("../data/TCGA_harmonized.txt", sep=";")

supertreat = pd.DataFrame(data={"case_uuid": clin["Patient_ID"]})



# filter file_dict by supertreat cases
file_dict = {k: v for k, v in file_dict.items() if k in supertreat["case_uuid"].values}

# invert the dictionary to mapp file names to file UUIDs later
inv_file_dict = {v: k for k, v in file_dict.items()}

# GDC API endpoint for files
files_endpt = "https://api.gdc.cancer.gov/files"

# filter by file_name using all file names from the manifest file
filters = {
        "op": "=",
        "content": {
            "field": "file_name",
            "value": list(file_dict.values())
        }
}

params = {
   "filters": json.dumps(filters),
   "size": "1000"
    }


# download all files metadata from GDC to find the file UUIDs 
response = requests.post(files_endpt, headers = {"Content-Type": "application/json"}, json = params)

files_metadata = response.json()
len(files_metadata["data"]["hits"])

# download files

# gene expression data format
# each column will be identified with gene_id 
# we will save unstranded, tpm_unstranded, fpkm_unstranded, fpkm_uq_unstranded in separate files
# we will keep the mapping between gene_id and gene_name in a separate file, together with gene_type

type_of_counts = "unstranded"

gene_mapping = pd.DataFrame(columns = ["gene_id", "gene_name", "gene_type"])

gene_expression = pd.DataFrame()

number_of_files = len(files_metadata["data"]["hits"])

for n, case in enumerate(files_metadata["data"]["hits"]):
    print("Processing: {} of {}".format(n + 1, number_of_files))

    file_uuid = case["file_id"]
    data_endpt = "https://api.gdc.cancer.gov/data/{}".format(file_uuid)
    response = requests.get(data_endpt,  headers = {"Content-Type": "application/json"})

    # select only the columns we need
    df = pd.read_csv(io.StringIO(response.text), sep="\t", comment="#") 

    if not set(df["gene_id"].values).issubset(gene_expression.columns) and not gene_expression.empty:
        print("Warning: New gene id found, NaN values will be added to the dataframe for previous cases.")

    data = dict(zip(df["gene_id"].values, df[type_of_counts].values))
    gene_expression_temp = pd.DataFrame(data = data, index = [inv_file_dict[case["file_name"]]] )
    gene_expression = pd.concat([gene_expression, gene_expression_temp])

    gene_mapping_temp = pd.DataFrame(
                        data = {"gene_id": df["gene_id"].values, 
                                "gene_name": df["gene_name"].values, 
                                "gene_type": df["gene_type"].values}
                                )

    gene_mapping = pd.concat([gene_mapping, gene_mapping_temp])
    gene_mapping.drop_duplicates(inplace=True)
    # test if the values in data match with the ones in df["unstranded"]

    

gene_expression.index.name = "Patient_ID"

gene_expression.to_csv("../data/{}.csv".format(type_of_counts), sep=";")


gene_mapping.to_csv("../data/gene_mapping.csv", sep=";")