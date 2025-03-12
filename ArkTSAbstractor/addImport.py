import os
import json
import re
from tqdm import tqdm

def process_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"File {file_path} content is not a list")

        updated_data = []

        for item in data:
            if not isinstance(item, list) or len(item) != 2:
                print(f"Warning: Skipping invalid item {item}")
                continue

            imports, code_str = item

            full_imports = []

            for imp in imports:
                component_name = imp['component_name']
                alias = imp['alias']
                search_term = alias if alias else component_name

                if re.search(r'\b' + re.escape(search_term) + r'\b', code_str):
                    full_imports.append(imp['full_import'])

            if full_imports:
                code_str = '\n'.join(full_imports) + '\n' + code_str

            updated_data.append(code_str)

        output_dir = os.path.join(os.path.dirname(file_path), 'processed')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, os.path.basename(file_path))

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)

        print(f"Processed file saved to: {output_file}")

    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")

def process_directory(directory):
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        return

    for root, dirs, files in os.walk(directory):
        for file in tqdm(files):
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                process_json_file(file_path)

if __name__ == "__main__":
    directory = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/import_function'  # Replace with your directory path
    process_directory(directory)
    # file_path = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/import_function'
    # process_json_file(file_path)