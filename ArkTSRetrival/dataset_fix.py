import json
from tqdm import tqdm
import os
import os
import json
import re
import argparse



def process_file(file_path, mode="both"):
    if os.path.isdir(file_path):
        print(f"Skipping directory: {file_path}")
        return [], []

    uis, funcs = process_out_json_file(file_path)
    if uis is None or funcs is None:
        print(f"Error processing file {file_path}")
        return [], []

    ui_res = []
    func_res = []

    for data in tqdm(uis):
        code = remove_comments_from_string(data['content'])
        ai_res = get_generation(code)
        if ai_res:
            ui_res.append({
                "query": ai_res['instructions'],
                "description": ai_res['description'],
                "code": ai_res['code'],
                "imports": data["imports"],
                "variables": data["variables"],
                "solution": code
            })

    for data in tqdm(funcs):
        code = remove_comments_from_string(data['content'])
        ai_res = get_generation(code)
        if ai_res:
            func_res.append({
                "query": ai_res['instructions'],
                "description": ai_res['description'],
                "code": ai_res['code'],
                "imports": data["imports"],
                "variables": data["variables"],
                "solution": code
            })


    return ui_res, func_res

def process_folder(folder_path, output_folder):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        output_path = os.path.join(output_folder, file)

        if os.path.exists(output_path):
            print(f"File {output_path} already exists, skipping...")
            continue
        ui_res, func_res = process_file(file_path)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        print(f"Saving results to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "ui_code": ui_res,
                "functions": func_res
            }, f, indent=2, ensure_ascii=False)

def process_root(root_path, out_path):
    for folder in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder)
        if os.path.isdir(folder_path):
            base_path = os.path.basename(folder_path)
            out_sub_path = os.path.join(out_path, base_path)
            process_folder(folder_path, out_sub_path)



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

def remove_comments_from_string(code_str):
    """
    从代码字符串中删除所有注释
    
    Args:
        code_str (str): 包含代码的字符串
    
    Returns:
        str: 删除注释后的代码字符串
    """
    # 首先处理多行注释
    code_str = re.sub(r'/\*[\s\S]*?\*/', '', code_str)
    
    # 处理单行注释
    # 将代码按行分割
    lines = code_str.split('\n')
    # 删除每行中//后面的内容
    cleaned_lines = []
    for line in lines:
        # 查找不在字符串中的 //
        result = ''
        in_string = False
        string_char = None  # 用于跟踪字符串的引号类型
        i = 0
        while i < len(line):
            if line[i] in ['"', "'"]:
                if not in_string:
                    in_string = True
                    string_char = line[i]
                elif string_char == line[i] and line[i-1] != '\\':
                    in_string = False
                result += line[i]
            elif line[i:i+2] == '//' and not in_string:
                break
            else:
                result += line[i]
            i += 1
        cleaned_lines.append(result.rstrip())
    
    # 重新组合代码，删除多余的空行
    result = '\n'.join(line for line in cleaned_lines if line.strip())
    return result

    
if __name__ == '__main__':
    process_root("/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/out", "./output_0415")