import os
import shutil
import json
import glob

# Set your root directory containing all the ID folders
PARENT_DIR = ""     # <--- change this to your actual master directory path
JSON_FILE = "/sluzba_ids.json" # <--- change this to your actual master directory path where sluzba_ids.json is located
# Directory where matching text files will be copied
TARGET_DIR = "data"

# Load the list of IDs from the JSON file
with open(JSON_FILE, 'r', encoding='utf-8') as f:
    ids = json.load(f)

# Create the target directory if it doesn't already exist
os.makedirs(TARGET_DIR, exist_ok=True)

# Iterate over each ID from the JSON
for _id in ids:
    # Construct the path to the 'Documents' subfolder for this ID
    docs_folder = os.path.join(PARENT_DIR, str(_id), "Documents")
     # Define the filename pattern to match relevant text files
    pattern = os.path.join(docs_folder, "popisyRealizacePoskytovaniSluzby_*_text.txt")
    # Use glob to find all files matching the pattern
    for file_path in glob.glob(pattern):
        if os.path.isfile(file_path):
            # Build the destination path in the target directory
            dest_path = os.path.join(TARGET_DIR, os.path.basename(file_path))
            # Copy the file preserving metadata (timestamps, permissions)
            shutil.copy2(file_path, dest_path)
            # Log the operation to the console
            print(f"Copied: {file_path} -> {dest_path}")

print("Done!")




