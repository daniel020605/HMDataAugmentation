import os
import json
from tqdm import tqdm

def extract_and_save(json_file, functions_dir, ui_code_dir):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        file_name = os.path.basename(json_file)
        base_name, _ = os.path.splitext(file_name)

        # Save functions if not empty
        functions = [item.get('functions', []) for item in data if item.get('functions')]
        if functions:
            functions_file = os.path.join(functions_dir, f"{base_name}_functions.json")
            with open(functions_file, 'w', encoding='utf-8') as f_func:
                json.dump(functions, f_func, indent=2, ensure_ascii=False)

        # Save ui_code if not empty
        ui_code = [item.get('ui_code', []) for item in data if item.get('ui_code')]
        if ui_code:
            ui_code_file = os.path.join(ui_code_dir, f"{base_name}_ui_code.json")
            with open(ui_code_file, 'w', encoding='utf-8') as f_ui:
                json.dump(ui_code, f_ui, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"Error processing file {json_file}: {str(e)}")

def process_directory(directory, functions_dir, ui_code_dir):
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        return

    os.makedirs(functions_dir, exist_ok=True)
    os.makedirs(ui_code_dir, exist_ok=True)

    for root, _, files in os.walk(directory):
        for file in tqdm(files):
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                extract_and_save(file_path, functions_dir, ui_code_dir)

if __name__ == "__main__":
    directory = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/data/projects_abstracted'  # Replace with your directory path
    functions_dir = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/functions'  # Replace with your functions directory path
    ui_code_dir = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/UI'  # Replace with your ui_code directory path

    process_directory(directory, functions_dir, ui_code_dir)