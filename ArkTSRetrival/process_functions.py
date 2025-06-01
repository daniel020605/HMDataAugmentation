#!/usr/bin/env python3
import os
import json
import re
from tqdm import tqdm
import argparse
from difflib import SequenceMatcher

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
    lines = code_str.split('\n')
    cleaned_lines = []
    for line in lines:
        result = ''
        in_string = False
        string_char = None
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
    
    return '\n'.join(line for line in cleaned_lines if line.strip())

def is_similar(a, b, threshold=0.9):
    """
    判断两个函数是否相似
    """
    # 首先去除两个函数中的注释
    a_clean = remove_comments_from_string(a)
    b_clean = remove_comments_from_string(b)
    return SequenceMatcher(None, a_clean, b_clean).ratio() > threshold

def process_json_file(file_path, threshold=0.9, dry_run=False):
    """
    处理单个JSON文件，去除注释并去重
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError(f"文件 {file_path} 的内容不是列表格式")

        # 用于存储唯一的函数对
        unique_pairs = []
        
        print(f"\n处理文件: {file_path}")
        for item in tqdm(data):
            if not isinstance(item, list) or len(item) != 2:
                print(f"警告: 跳过无效的数据项 {item}")
                continue
                
            imports, func = item
            # 检查这个函数是否与已存在的函数相似
            is_duplicate = False
            for existing_pair in unique_pairs:
                if is_similar(func, existing_pair[1], threshold):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_pairs.append([imports, func])

        if not dry_run:
            # 创建输出目录
            output_dir = os.path.join(os.path.dirname(file_path), 'processed')
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存处理后的文件
            output_file = os.path.join(output_dir, os.path.basename(file_path))
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(unique_pairs, f, indent=2, ensure_ascii=False)
            
            print(f"\n处理完成:")
            print(f"原始函数数量: {len(data)}")
            print(f"去重后函数数量: {len(unique_pairs)}")
            print(f"输出文件保存至: {output_file}")
        else:
            print(f"\n预览模式:")
            print(f"原始函数数量: {len(data)}")
            print(f"去重后函数数量: {len(unique_pairs)}")
            
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='处理JSON文件中的函数：去除注释并去重')
    parser.add_argument('directory', help='包含JSON文件的目录路径')
    parser.add_argument('--threshold', type=float, default=0.9, 
                      help='函数相似度阈值 (0.0-1.0), 默认为0.9')
    parser.add_argument('--dry-run', action='store_true', 
                      help='预览模式，不实际修改文件')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误：目录 '{args.directory}' 不存在")
        return
    
    # 遍历目录中的所有JSON文件
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                process_json_file(file_path, args.threshold, args.dry_run)

if __name__ == "__main__":
    main() 