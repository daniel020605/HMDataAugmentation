import os
import json
from tqdm import tqdm

def extract_and_save(json_file, output_dir):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        file_name = os.path.basename(json_file)
        base_name, _ = os.path.splitext(file_name)
        folder_path = os.path.join(output_dir, base_name)
        os.makedirs(folder_path, exist_ok=True)

        for item in data:
            file_path = item['file']
            file_basename = os.path.basename(file_path)
            output_file = os.path.join(folder_path, f"{file_basename}.json")

            content = {
                'imports': item.get('imports', []),
                'variables': item.get('variables', []),
                'ui_code': [item.get('content') for item in item.get('ui_code', [])],
                'functions': [item.get('content') for item in item.get('functions', [])]
            }

            with open(output_file, 'w', encoding='utf-8') as out_f:
                json.dump(content, out_f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"Error processing file {json_file}: {str(e)}")

def process_directory(directory, output_dir):
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        return

    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(directory):
        for file in tqdm(files):
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                extract_and_save(file_path, output_dir)

if __name__ == "__main__":
    directory = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/data/projects_abstracted'  # Replace with your directory path
    output_dir = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/out'  # Replace with your output directory path

    process_directory(directory, output_dir)