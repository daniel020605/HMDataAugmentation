import os
import json

from tqdm import tqdm


def collect_ui_code_and_functions(root_folder):
    all_ui_code = []
    all_functions = []

    for subdir, _, files in tqdm(os.walk(root_folder)):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_ui_code.extend(data.get('ui_code', []))
                    all_functions.extend(data.get('functions', []))

    return all_ui_code, all_functions

def save_to_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    root_folder = '/Users/liuxuejin/Desktop/Projects/PythonTools/output_0415'
    ui_code_output_file = './dataset_ui_code_0505.json'
    functions_output_file = './dataset_functions_0505.json'

    all_ui_code, all_functions = collect_ui_code_and_functions(root_folder)
    save_to_file(all_ui_code, ui_code_output_file)
    save_to_file(all_functions, functions_output_file)