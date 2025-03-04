import os
import json

def count_ui_code_and_functions(folder_path):
    total_ui_code_count = 0
    total_function_count = 0

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # 遍历每个JSON对象
                    for item in data:
                        # 统计ui_code数量
                        if 'ui_code' in item:
                            total_ui_code_count += len(item['ui_code'])
                        # 统计functions数量
                        if 'functions' in item:
                            total_function_count += len(item['functions'])
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return total_ui_code_count, total_function_count

def load_reserved_words():
    reserved_words = set()
    with open("./reserved_word.txt", "r") as file:
        for line in file:
            reserved_words.add(line.strip())
    return reserved_words

if __name__ == "__main__":
    folder_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/analysis_results"
    ui_code_count, function_count = count_ui_code_and_functions(folder_path)
    print(f"总的 ui_code 数量: {ui_code_count}")
    print(f"总的 functions 数量: {function_count}")
