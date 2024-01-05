import os
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError
import glob
from pathlib import Path
import shutil


# Constants
BUCKET_NAME = 'vast4elephant'
S3_PREFIX = 'json/arXiv/CL/'
TEMP_DIR = '/tmp'

#START HERE: you are writing a thing to get the correct storage location for the s3 files
current_path = Path(__file__).resolve()
project_root = current_path.parent.parent  # Assuming this script is one level below the project root
# while project_root != current_path.root and not (project_root / '.venv').exists():
#     project_root = project_root.parent

STORAGE_DIR = project_root / 'storage'


# Initialize S3 client
s3 = boto3.client('s3')

def download_files():
    try:
        # List files in the specified S3 path
        objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_PREFIX)['Contents']
        
        for obj in objects:
            key = obj['Key']
            if key.endswith('.json.gz'):
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
      gz_files = glob.glob(f"{TEMP_DIR}/*.json.gz")

      for file_path in gz_files:
            # Unzip each file
            subprocess.run(["gunzip", file_path])
            print(f"Unzipped {file_path}")
    except Exception as e:
        print(f"Error: {e}")

def copy_to_storage():
    try:
        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)
            print(f"Created directory {STORAGE_DIR}")

        for file in os.listdir(TEMP_DIR):
            if file.endswith('.json'):
                source_path = os.path.join(TEMP_DIR, file)
                destination_path = os.path.join(STORAGE_DIR, file)

                # Move file to the storage directory, overwrite if file already exists
                shutil.move(source_path, destination_path)
                print(f"Moved {file} to {STORAGE_DIR}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_files()
    unzip_files()
    copy_to_storage()
