#!/usr/bin/python3
# Amazon Security Lake Quicksight Asset Deployment Tool
from pathlib import Path
import os
import sys
import shutil
import argparse

cliparser = argparse.ArgumentParser( description="Amazon Quicksight Asset Deployment Tool")
cliparser.add_argument('--account', help="Amazon account ID")                   # used for api calls and sanitize
cliparser.add_argument('--region', help="Amazon account region")                # used for sanitize
cliparser.add_argument('--principal', help="Amazon Security Lake region")        # used for Amazon Security Lake
args = cliparser.parse_args()

aws_region = args.region
aws_account_id = args.account
aws_principal_id = args.principal
    
def main(aws_region, aws_account_id, aws_principal_id):

    """
    # The main function in this script will take a users input
    # '-i /path/to/some/file/file.parquet' and search for parquet
    # if the schema is valid OCSF
    """

    # Store the absolute path of this script in path variable
    BASE_DIR = str((Path(os.path.abspath(__file__))).parent).replace('\\', '/')

    # Set relative path values for script runtime
    TEMPLATES_DIR = BASE_DIR + '/asset-templates/'
    SCRIPTS_DIR = BASE_DIR + '/scripts/'
    STAGING_DIR = BASE_DIR + '/qs-lake-staging/'
    
    # Recursive search for all files with .json extension in input directory path
    pathlist = Path(TEMPLATES_DIR).glob('*.json')
    files = os.listdir(TEMPLATES_DIR)
    
    # Fetching all the files to directory
    for file_name in files:
       shutil.copy(TEMPLATES_DIR+file_name, STAGING_DIR+file_name)
       os.system(f"python {SCRIPTS_DIR}qstool.py --verbose --assets {STAGING_DIR+file_name} sanitize all --principal {aws_principal_id}  --region {aws_region} --account {aws_account_id}")
       os.system(f"python {SCRIPTS_DIR}qstool.py --verbose --assets {STAGING_DIR+file_name} delete all --confirm -i")
       
    for file_name in files:
       shutil.copy(TEMPLATES_DIR+file_name, STAGING_DIR+file_name)
       os.system(f"python {SCRIPTS_DIR}qstool.py --verbose --assets {STAGING_DIR+file_name} sanitize all --principal {aws_principal_id}  --region {aws_region} --account {aws_account_id}")
       os.system(f"python {SCRIPTS_DIR}qstool.py --verbose --assets {STAGING_DIR+file_name} create all -i")
       
if __name__ == '__main__':

    main(aws_region, aws_account_id, aws_principal_id)


