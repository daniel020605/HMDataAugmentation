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

def count_json_items_in_folder(folder_path):
    total_json_items = 0
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    total_json_items += len(data)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    return total_json_items

def load_reserved_words():
    reserved_words = set()
    with open("./reserved_word.txt", "r") as file:
        for line in file:
            reserved_words.add(line.strip())
    return reserved_words

import shutil


def extract_and_rename_folders(base_folder):
    for folder_b in os.listdir(base_folder):
        path_b = os.path.join(base_folder, folder_b)
        if os.path.isdir(path_b):
            for folder_c in os.listdir(path_b):
                path_c = os.path.join(path_b, folder_c)
                if os.path.isdir(path_c):
                    new_name = f"{folder_b}_{folder_c}"
                    new_path = os.path.join(base_folder, new_name)
                    shutil.move(path_c, new_path)

def delete_empty_folders(base_folder):
    for folder in os.listdir(base_folder):
        path = os.path.join(base_folder, folder)
        if os.path.isdir(path):
            if not os.listdir(path):
                os.rmdir(path)


def find_file_by_name(directory, filename):
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None

import re
def remove_comments(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 移除双斜杠注释
    content = re.sub(r'//.*', '', content)
    # 移除星号注释
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def check_project_version(directory):
    profile = find_file_by_name(directory, 'build-profile.json5')
    if profile:
        with open(profile, 'r', encoding='utf-8') as file:
            content = file.read()
            version_pattern = re.compile(r'(("compileSdkVersion")|("compatibleSdkVersion"))\s?:\s*((\d+)|"([\d.()]+)")')
            for match in version_pattern.finditer(content):
                if match.group(5) and match.group(5).strip().isnumeric():
                    if int(match.group(5)) < 10:
                        print(f"跳过项目 {directory}: 不支持的版本 {match.group(5)}")
                        return False
                    else:
                        return True
                elif match.group(6) and match.group(6).strip():
                    if match.group(6).strip() == '5.0.0(12)' or match.group(6).strip() == '5.0.1(13)' or match.group(6).strip() == '5.0.2(14)' or match.group(6).strip() == '5.0.3(15)':
                        return True
                    else:
                        return False
    return False

def process_out_json_file(json_file, origin = False):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        imports = data.get('imports', [])
        variables = data.get('variables', [])
        ui_code = data.get('ui_code', [])
        functions = data.get('functions', [])

        ui_res = []
        func_res = []

        def merge_imports(import_list):
            import_dict = {}
            for imp in import_list:
                module_name = imp['module_name']
                component_name = imp['component_name']
                if module_name not in import_dict:
                    import_dict[module_name] = []
                import_dict[module_name].append(component_name)
            merged_imports = []
            for module_name, components in import_dict.items():
                merged_imports.append(f"import {{ {', '.join(components)} }} from '{module_name}';")
            return merged_imports

        # Check ui_code for matches
        for code in ui_code:
            import_statements = []
            variable_statements = []
            origin_flag = True
            for imp in imports:
                if imp['component_name'] in code:
                    if origin:
                        if imp["module_name"].startswith("."):
                            origin_flag = False
                    import_statements.append(imp)
            if origin and not origin_flag:
                continue
            for var in variables:
                if var['name'] in code:
                    variable_statements.append(var['full_variable'])
            if import_statements or variable_statements:
                ui_res.append({
                    'content': code,
                    'imports': merge_imports(import_statements),
                    'variables': variable_statements
                })

        # Check functions for matches
        for func in functions:
            import_statements = []
            variable_statements = []
            origin_flag = True
            for imp in imports:
                if imp['component_name'] in func:
                    if origin:
                        if imp["module_name"].startswith("."):
                            origin_flag = False
                    import_statements.append(imp)
            if origin and not origin_flag:
                continue
            for var in variables:
                if var['name'] in func:
                    variable_statements.append(var['full_variable'])
            if import_statements or variable_statements:
                func_res.append({
                    'content': func,
                    'imports': merge_imports(import_statements),
                    'variables': variable_statements
                })

        return ui_res, func_res
    except Exception as e:
        print(f"Error processing file {json_file}: {str(e)}")
        return None, None
import json

def count_json_items(file_path):
    """
    统计 JSON 文件中的项数
    :param file_path: JSON 文件路径
    :return: 项数
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return len(data)
    except Exception as e:
        print(f"读取文件 {file_path} 时发生错误: {e}")
        return 0

if __name__ == "__main__":
    # folder_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/analysis_results"
    # ui_code_count, function_count = count_ui_code_and_functions(folder_path)
    # print(f"总的 ui_code 数量: {ui_code_count}")
    # print(f"总的 functions 数量: {function_count}")
    #
    # folder_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/code_classification/function"
    # print(count_json_items_in_folder(folder_path))
    #
    # # folder_path = "/Users/liuxuejin/Downloads/github_cloned_repos_1min_stars/19-CialloOpenHarmony"
    # # print(check_project_version(folder_path))
    # folder_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/complete_function"
    # print(count_json_items_in_folder(folder_path))
    #
    # # folder_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/function_with_import"
    # # print(count_json_items_in_folder(folder_path))
    #
    # folder_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/code_classification/UI"
    # print(count_json_items_in_folder(folder_path))
    #
    # folder_path = "/Users/liuxuejin/Desktop/Projects/PythonTools/test/UIOut"
    # print(count_json_items_in_folder(folder_path))
    #
    # folder_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/function_with_import_plain_ORIGIN_ONLY"
    # print(count_json_items_in_folder(folder_path))
    file_path = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/CD_code_description_0423.json"
    print(count_json_items(file_path))
    file_path = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/CD_UI_code_description_0423.json"
    print(count_json_items(file_path))
    file_path = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/EG_code_description.json"
    print(count_json_items(file_path))
    file_path = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/EG_generate_instruction.json"
    print(count_json_items(file_path))
    file_path = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/IC_dataset_functions_match.json"
    print(count_json_items(file_path))
    file_path = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/IC_dataset_ui_code_0401.json"
    print(count_json_items(file_path))
    file_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/dataset_functions_0505.json"
    print(count_json_items(file_path))
    file_path = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/dataset_ui_code_0505.json"
    print(count_json_items(file_path))