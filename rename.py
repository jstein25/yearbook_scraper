"""
A file for renaming yearbooks in the input directory.
"""

import os
import re
from dotenv import load_dotenv

load_dotenv()
input_dir = os.getenv("INPUT_DIR")

def rename_to_stats():
    for file_name in os.listdir(input_dir):
        old_path = os.path.join(input_dir, file_name)
        if os.path.isfile(old_path):
            new_name = file_name.replace("education", "statistical")
            new_path = os.path.join(input_dir, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed: {file_name} -> {new_name}")

def year_plus_one():
    for file_name in os.listdir(input_dir):
        old_path = os.path.join(input_dir, file_name)
        if os.path.isfile(old_path):
            match = re.search(r"(\d{4})", file_name)
            if match:
                year = int(match.group(1)) + 1
                new_name = file_name.replace(match.group(1), str(year))
                new_path = os.path.join(input_dir, new_name)
                os.rename(old_path, new_path)
                print(f"Renamed: {file_name} -> {new_name}")

if __name__ == "__main__":
    year_plus_one()