#!/usr/bin/env python3
import os
import json
import re
import argparse

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

def process_json_file(file_path):
    """
    处理单个JSON文件
    
    Args:
        file_path (str): JSON文件的路径
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 递归处理所有字符串值
        def process_item(item):
            if isinstance(item, str):
                return remove_comments_from_string(item)
            elif isinstance(item, list):
                return [process_item(i) for i in item]
            elif isinstance(item, dict):
                return {k: process_item(v) for k, v in item.items()}
            return item
        
        processed_data = process_item(data)
        
        # 保存处理后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        print(f"已处理文件: {file_path}")
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='删除JSON文件中函数字符串里的注释')
    parser.add_argument('directory', help='包含JSON文件的目录路径')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际修改文件')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误：目录 '{args.directory}' 不存在")
        return
    
    # 遍历目录中的所有JSON文件
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                if args.dry_run:
                    print(f"将要处理文件: {file_path}")
                else:
                    process_json_file(file_path)

if __name__ == "__main__":
    main() 