import os
import json

def process_json_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            # Process the data
            new_data = [item[1] if len(item) > 1 else "" for item in data]
            
            # Write the modified data back to the file
            with open(file_path, 'w') as file:
                json.dump(new_data, file, indent=4)

# Example usage
# folder_path = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/complete_function'
# process_json_files(folder_path)

from difflib import SequenceMatcher
from tqdm import tqdm
res = []

def is_similar(a, b, threshold=0.9):
    global res
    res.append([SequenceMatcher(None, a, b).ratio(), a, b])
    return SequenceMatcher(None, a, b).ratio() > threshold

def remove_similar_strings(data, threshold=0.9):
    unique_data = []
    for item in tqdm(data):
        if not any(is_similar(item, unique_item, threshold) for unique_item in unique_data):
            unique_data.append(item)
    return unique_data

def do_json_files(folder_path, threshold=0.9):
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            # Process the data
            new_data = remove_similar_strings(data, threshold)
            
            # Write the modified data back to the file
            # with open(file_path, 'w') as file:
            #     json.dump(new_data, file, indent=4)
            # 将res按照相似度排序
            res.sort(key=lambda x: x[0], reverse=True)
            output_file = file_path.replace("/test", "/out").replace('.json', '_similarity.json')    
            with open(output_file, 'w') as file:
                json.dump(res, file, indent=4)

# Example usage
# folder_path = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/complete_function'
# folder_path = '/Users/liuxuejin/Desktop/Projects/PythonTools/test'
# do_json_files(folder_path)

import os
import json
from difflib import SequenceMatcher

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

# Example usage
# folder_path = '/Users/liuxuejin/Desktop/Projects/PythonTools/test'
# process_json_files(folder_path)
# import json
# import os
# with open ('extracted_pre_tags_with_instruction.json', 'r') as file:
#     data = json.load(file)
#     i = 0
#     for obj in data:
#         obj['id'] = i
#         i += 1
#     with open ('extracted_pre_tags_with_instruction copy.json', 'w') as file:
#         json.dump(data, file, indent=4, ensure_ascii= False)



def count_items_in_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return len(data)

# Example usage
file_path = 'output/IC_dataset_functions_match.json'
print(f"Number of items in the JSON file: {count_items_in_json(file_path)}")