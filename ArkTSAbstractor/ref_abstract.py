import re
from bs4 import BeautifulSoup
import os

def extract_pre_with_context(file_path, start_id=1):
    # 打开并读取 HTML 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有 class='\"section\"' 的 div 标签
    sections = soup.find_all('div', class_='section')

    # 提取每个 section 中的 <pre> 标签及其上下文
    extracted_data = []
    current_id = start_id
    import_module = None
    for section in sections:
        pre = section.find('pre', class_=["typescript", "screen", "ts"])
        if pre:
            parent = pre.parent  # 父标签
            pre.extract()
            if pre.get("class") == ["screen"] and not "{" in pre.text:
                print(f"Warning: <pre> tag text length is less than 24 characters in {file_path}.")
                continue
            if any(substring in parent.text for substring in ["导入模块"]) or (len(pre.text) <= 64 and "{" in pre.text):
                doc_type = "Import"
                import_module = pre.text
            else:
                doc_type = "Reference"

            if "Java" in parent.text or "java" in pre.text:
                continue
            if parent.text.__len__() <= 48 and any(substring in parent.text for substring in ["示例：", "请求示例", "响应示例"]):
                parent = parent.parent  # 如果父标签文本长度小于100，则获取父标签的父标签
            # 从父标签中删除 <pre> 标签
            # 获取父标签的字符串表示
            function_pattern = re.compile(
            r'(\w+\s)?(\w+\s?)(=\s?)?\(\s?((\.\.\.)?((\w+\??\s?:\s?[^)]+\s?)(,\s?\w+\??\s?:\s?[^)]+)*)?)\)\s*?\s?(=>\s?)?(:\s?\w+\s?)?')
            function_call = None
            for match in function_pattern.finditer(str(parent)):
                function_call = match.group(0).strip() if match.group(0) else None
            
            h4 = parent.find('h4')
            function_name = h4.text if h4 else None
            extracted_data.append({
                "id": current_id,  # 添加自增主键
                "pre": pre.text,
                "type": doc_type,
                "function_call": function_call,
                "function_name": function_name,
                "parent_text": parent.text,
                "import_module": import_module if doc_type == "Reference" else None,
                "parent": str(parent),
                "file_path": file_path,
            })
            current_id += 1

    return extracted_data, current_id

import json
def process_html_folder(folder_path, output_file):
    # 打开输出文件
    with open(output_file, 'w', encoding='utf-8') as output:
        # 遍历文件夹中的所有文件
        res = []
        current_id = 1  # 初始化自增主键
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    print(f"Processing file: {file_path}")
                    
                    # 提取 <pre> 标签及其上下文
                    extracted_data, current_id = extract_pre_with_context(file_path, current_id)
                    if len(extracted_data) == 0:
                        print(f"Warning: No <pre> tags found in {file_path}")
                    else:
                        res.extend(extracted_data)
                    # 保存提取的内容到JSON文件
        output.write(json.dumps(res, ensure_ascii=False, indent=4) + '\n')
        print(f"Extracted {len(res)} <pre> tags in total.")

if __name__ == "__main__":
    # 指定 HTML 文件夹路径
    # folder_names = ["harmonyos-faqs", "harmonyos-guides", "harmonyos-releases", "best-practices"]
    # # folder_names = ["harmonyos-references"]
    # for folder_name in folder_names:
    #     folder_path = f"/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/{folder_name}"
    #     # 指定输出文件路径
    #     output_file = f"/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/extracted_{folder_name}.json"
    #
    #     # 处理文件夹中的所有 HTML 文件并保存结果
    #     process_html_folder(folder_path, output_file)
    folder_path = "/Users/liuxuejin/Desktop/Projects/PythonTools/html_pages"
    output_file = "/Users/liuxuejin/Desktop/Projects/PythonTools/extracted_ui_module.json"
    process_html_folder(folder_path, output_file)