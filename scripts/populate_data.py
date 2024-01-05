import os
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError
import glob
from pathlib import Path
import shutil
import argparse


parser = argparse.ArgumentParser(description='Download and process S3 files.')
parser.add_argument('type', type=str, help='Document type extension')
args = parser.parse_args()
# Constants
BUCKET_NAME = 'vast4elephant'
DOC_TYPE = 'json' 
if args.type: 
  DOC_TYPE = args.type 
DOC_TYPE_EXT = DOC_TYPE
print("doc type ext", DOC_TYPE_EXT)
S3_PREFIX = f'{DOC_TYPE}/arXiv/CL/'
TEMP_DIR = '/tmp'

known_types = ['text', 'json']
#throw an error if the DOC_TYPE is not in the known list of types
if DOC_TYPE not in known_types:
  raise ValueError(f"Unknown document type: {DOC_TYPE}")
if DOC_TYPE == 'text':
    DOC_TYPE_EXT = 'txt'

#START HERE: you are writing a thing to get the correct storage location for the s3 files
current_path = Path(__file__).resolve()
project_root = current_path.parent.parent  # Assuming this script is one level below the project root
# while project_root != current_path.root and not (project_root / '.venv').exists():
#     project_root = project_root.parent

STORAGE_DIR = project_root / 'storage'
DOC_TYPE_DIR = STORAGE_DIR / DOC_TYPE


# Initialize S3 client
s3 = boto3.client('s3')

def download_files():
    try:
        # List files in the specified S3 path
        objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_PREFIX)['Contents']
        
        for obj in objects:
            key = obj['Key']
            if key.endswith(f'.{DOC_TYPE_EXT}.gz'):
                # Download file to temp directory
                s3.download_file(BUCKET_NAME, key, os.path.join(TEMP_DIR, os.path.basename(key)))
                print(f"Downloaded {key} to {TEMP_DIR}")

    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error: {e}")

def unzip_files():
    try:
        # Unzip all .gz files in the temp directory
      gz_files = glob.glob(f"{TEMP_DIR}/*.{DOC_TYPE_EXT}.gz")

      for file_path in gz_files:
            # Unzip each file
            subprocess.run(["gunzip", file_path])
            print(f"Unzipped {file_path}")
    except Exception as e:
        print(f"Error: {e}")

def copy_to_storage():
    try:
        if not os.path.exists(DOC_TYPE_DIR):
            os.makedirs(DOC_TYPE_DIR)
            print(f"Created directory {DOC_TYPE_DIR}")

        for file in os.listdir(TEMP_DIR):
            if file.endswith(f'.{DOC_TYPE_EXT}'):
                source_path = os.path.join(TEMP_DIR, file)
                destination_path = os.path.join(DOC_TYPE_DIR, file)

                # Move file to the storage directory, overwrite if file already exists
                shutil.move(source_path, destination_path)
                print(f"Moved {file} to {DOC_TYPE_DIR}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_files()
    unzip_files()
    copy_to_storage()
