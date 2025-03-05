import os
import json
from tqdm import tqdm

test_ui_path = './code_classification/test_UI'
test_function_path = './code_classification/test_function'
ui_path = './code_classification/UI'
function_path = './code_classification/function'

def classify_code(folder_path):
    # 遍历文件夹中的所有文件
    for filename in tqdm(os.listdir(folder_path)) :
        test_function_codes = []
        test_ui_codes = []
        ui_codes = []
        function_codes = []
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # 遍历每个JSON对象
                    for item in data:
                        if 'file' in item:
                            est_file_path = item['file']
                            if 'test' in est_file_path or 'Test' in est_file_path:
                                if 'ui_code' in item and item['ui_code']:
                                    test_ui_codes.extend(item['ui_code'])
                                if 'functions' in item and item['functions']:
                                    test_function_codes.extend(item['functions'])
                            else:
                                if 'ui_code' in item and item['ui_code']:
                                    ui_codes.extend(item['ui_code'])
                                if 'functions' in item and item['functions']:
                                    function_codes.extend(item['functions'])
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
            if len(test_ui_codes) > 0:
                if not os.path.exists(test_ui_path):
                    os.makedirs(test_ui_path)
                with open(os.path.join(test_ui_path, f'{filename}'), 'w') as f:
                    json.dump(test_ui_codes, f, indent=4, ensure_ascii=False)
            if len(test_function_codes) > 0:
                if not os.path.exists(test_function_path):
                    os.makedirs(test_function_path)
                with open(os.path.join(test_function_path, f'{filename}n'), 'w') as f:
                    json.dump(test_function_codes, f, indent=4, ensure_ascii=False)
            if len(ui_codes) > 0:
                if not os.path.exists(ui_path):
                    os.makedirs(ui_path)
                with open(os.path.join(ui_path, f'{filename}'), 'w') as f:
                    json.dump(ui_codes, f, indent=4, ensure_ascii=False)
            if len(function_codes) > 0:
                if not os.path.exists(function_path):
                    os.makedirs(function_path)
                with open(os.path.join(function_path, f'{filename}'), 'w') as f:
                    json.dump(function_codes, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    folder_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/analysis_results"
    classify_code(folder_path)

