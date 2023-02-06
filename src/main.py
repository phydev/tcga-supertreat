# download TCGA data from GDC using the GDC API
# https://docs.gdc.cancer.gov/API/Users_Guide/Getting_Started/
# we have a manifest file with all the file names and UUIDs
# we have a list of case UUIDs for the supertreat cases
# we need to download the file info for each case and link the file UUID to the case UUID
# then we need to download the files keeping the original file names

import pandas as pd
import requests
import json

manifest_file = 'data/manifest.json'

# open manifest file with file names and UUIDs
with open(manifest_file) as file:

    # load json file as a dictionary
    manifest = json.load(file)

# create a dictionary with file UUIDs as keys and file names as values
file_dict = {}

for file in manifest:
    file_dict[file["cases"][0]["case_id"]] = file['file_name']

# load supertreat case ids
supertreat = pd.read_csv('data/supertreat_cases.csv')

# filter file_dict by supertreat cases
file_dict = {k: v for k, v in file_dict.items() if k in supertreat["case_uuid"].values}

# I need to download the file info for each case and link the file UUID to the case UUID

files_endpt = "https://api.gdc.cancer.gov/files"

# filter by file_name using all file names from the manifest file
params = {
    "filters": {
        "op": "in",
        "content": {
            "field": "file_name",
            "value": list(file_dict.values())
        }
    }
}

# download all files metadata from GDC to find the file UUIDs 
response = requests.post(files_endpt, headers = {"Content-Type": "application/json"}, json = params)

files_metadata = response.json()

# download the files

for case in files_metadata["data"]["hits"]:

    file_uuid = case["file_id"]
    data_endpt = "https://api.gdc.cancer.gov/data/{}".format(file_uuid)
    response = requests.get(data_endpt,  headers = {"Content-Type": "application/json"})
   
    # we can process the files here, by selecting only the columns we need
    # for now we will just save them to disk
    # save the file
    
    file = open(case["file_name"], "w")
    file.write(response.text)
    file.close()