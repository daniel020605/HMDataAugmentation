from tqdm import tqdm
import os
import json
from difflib import SequenceMatcher
import argparse

def is_similar(a, b, threshold=0.9):
    return SequenceMatcher(None, a, b).ratio() > threshold

def remove_similar_strings(data, threshold=0.9):
    unique_data = []
    for item in tqdm(data):
        if not any(is_similar(item, unique_item, threshold) for unique_item in unique_data):
            unique_data.append(item)
    return unique_data

def process_json_files(folder_path):
    for filename in tqdm(os.listdir(folder_path)):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)

            # Remove similar strings
            data = remove_similar_strings(data)
            
            # Write the modified data back to the file
            output_folder = os.path.join(folder_path, 'out')
            os.makedirs(output_folder, exist_ok=True)
            output_file = os.path.join(output_folder, filename)
            with open(output_file, 'w') as file:
                json.dump(data, file, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON files to remove similar strings.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing JSON files.")
    args = parser.parse_args()
    
    process_json_files(args.folder_path)