import os
import regex as re
import json

"""
    给出一个用于提取 ArkUI 页面代码的脚本函数。
"""

# 存储提取结果的目录
OUTPUT_DIR = 'ArkTS_UICode'

# 创建输出目录（如果不存在）
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

extracted_functions = {}

# 扫描目录并提取内容
def scan_and_extract(directory):
    """
    遍历给定的目录，扫描 .ets 文件，并提取其中的 `build()` 函数和 `@Builder` 注解的函数内容。
    :param directory: 项目根目录的路径
    """
    for root, dirs, files in os.walk(directory):
        # 忽略 'build' 和 'oh_modules' 文件夹
        dirs[:] = [d for d in dirs if d not in ['build', 'oh_modules']]
        for file in files:
            # 只处理.ets文件，且文件路径必须包含 'main/ets/pages' 或 'main/ets/component'
            if file.endswith('.ets') and any(os.path.join('main', 'ets', sub_dir) in os.path.relpath(root, directory) for sub_dir in [ 'pages', 'component']):

                file_path = os.path.join(root, file)
                extract_and_save(file_path, directory)

# 提取build()函数和@Builder注解的内容
def extract_and_save(file_path, project_directory):
    """
    从指定文件中提取 `build()` 函数和 `@Builder` 注解的内容，并存储到字典中。
    :param file_path: 文件的路径
    :param project_directory: 项目根目录的路径，用于计算相对路径
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找所有build()函数
    build_functions = find_function(content, 'build')

    # 查找所有@Builder注解及其函数体
    builder_annotations = find_annotation(content, '@Builder')

    if build_functions or builder_annotations:
        # 将内容存储到字典中，以文件路径为键
        functions_content = []

        # 如果有build函数，添加到函数内容列表
        if build_functions:
            for build_func in build_functions:
                functions_content.append({
                    'function_name': 'build',
                    'content': build_func
                })

        if builder_annotations:
            for builder_annotation in builder_annotations:
                # 正则提取函数名（注解后的第一个函数名）
                match = re.search(r'@Builder\s+(?:[\w\s]+?\s+)?(\w+)\(\)', builder_annotation)
                if match:
                    function_name = match.group(1)  # 使用 group(1) 提取函数名
                    functions_content.append({
                        'function_name': function_name,
                        'content': builder_annotation
                    })

        # 保存到字典，文件路径相对于项目根目录
        relative_path = os.path.relpath(file_path, start=project_directory)
        extracted_functions[relative_path] = functions_content

        print(f"Extracted content from {file_path}")

# 查找所有 @Builder 注解的函数，并返回它们的内容，包括嵌套的大括号
def find_annotation(text, annotation):
    """
    找到所有 @Builder 注解的函数，并返回它们的内容，包括嵌套的大括号。
    """
    escaped_annotation = re.escape(annotation)

    # 用正则表达式匹配动态注解名称和函数头
    pattern = rf'({escaped_annotation}\s*([\w\d_]+\s*)+(\(\))*\s*\{{)'
    matches = []

    # 查找所有注解和函数头的位置
    for match in re.finditer(pattern, text):
        start_idx = match.start()  # @Builder 注解和函数名的位置
        # 从找到的位置开始，逐字符扫描，处理嵌套大括号
        brace_count = 0
        end_idx = start_idx
        while text[end_idx] != '{':
            end_idx += 1

        for i in range(end_idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1

            # 当大括号匹配完时，停止扫描
            if brace_count == 0:
                end_idx = i
                break

        # 提取完整的函数体，包括注解和函数头
        function_code = text[start_idx:end_idx + 1]
        matches.append(function_code)
    return matches

def find_function(text, function_name):
    """
    查找函数名为 function_name 的函数，并返回其内容，包括嵌套的大括号。
    """
    pattern = rf'{function_name}\(\)\s*\{{'  # 匹配函数头
    matches = []

    # 查找所有函数头的位置
    for match in re.finditer(pattern, text):
        start_idx = match.start()  # 函数头的位置

        # 从函数头的位置开始逐字符扫描，处理嵌套大括号
        brace_count = 0
        end_idx = start_idx
        while text[end_idx] != '{':
            end_idx += 1

        # 使用栈来处理大括号匹配
        for i in range(end_idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1

            # 当大括号匹配完时，停止扫描
            if brace_count == 0:
                end_idx = i
                break

        # 提取完整的函数体，包括函数头和注解
        function_code = text[start_idx:end_idx + 1]
        matches.append(function_code)

    return matches

def save_extracted_functions(project_directory):
    """
    将提取的函数内容保存到 JSON 文件中，文件名为项目根目录名称
    :param project_directory: 项目根目录的路径
    """
    project_name = os.path.basename(project_directory)
    output_json_path = os.path.join(OUTPUT_DIR, f'{project_name}_extracted_functions.json')

    # 如果没有找到任何函数内容，打印并退出
    if not extracted_functions:
        print("No relevant functions or annotations found.")
        return

    # 保存提取内容到JSON文件
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(extracted_functions, json_file, ensure_ascii=False, indent=4)

    print(f"All extracted functions and annotations have been saved to {output_json_path}")

def extract_functions_from_project(project_directory):
    """
    传入项目根目录路径，扫描该目录下的所有相关 .ets 文件，提取函数，并保存到JSON文件中
    :param project_directory: 项目根目录路径
    """
    scan_and_extract(project_directory)
    save_extracted_functions(project_directory)


if __name__ == "__main__":
    # 示例：直接传入项目的路径，调用接口提取函数
    project_path = r'C:\Users\sunguyi\Desktop\repos\github_5min_stars_projects\harmony-next-music-sharing_1'
    extract_functions_from_project(project_path)