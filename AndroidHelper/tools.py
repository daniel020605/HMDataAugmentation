import os

def check_files_in_functions_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if len(content) < 30:
                    print(f"File: {filename}")
                    print(content)
                    print("\n" + "="*50 + "\n")


def delete_empty_files_and_dirs(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path) and os.path.getsize(file_path) <= 10:
                os.remove(file_path)
                print(f"Deleted empty file: {file_path}")

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"Deleted empty directory: {dir_path}")


import os
import json


def count_functions_in_json_files(folder_path):
    total_count = 0

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)

            # 打开并读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                # 统计每个JSON文件中function数据的条数
                for functions in data.values():
                    total_count += len(functions)

    return total_count



if __name__ == "__main__":
    # functions_folder = './functions'
    # check_files_in_functions_folder(functions_folder)
    # delete_empty_files_and_dirs("./UI/")
    # 示例用法
    folder_path = './functions'
    print(f'Total function count: {count_functions_in_json_files(folder_path)}')