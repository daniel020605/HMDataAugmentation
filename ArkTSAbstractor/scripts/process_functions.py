#!/usr/bin/env python3
import os
import json
import re
from tqdm import tqdm
import argparse
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ProcessingStats:
    """处理统计信息"""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_functions: int = 0
    unique_functions: int = 0

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
    
    Args:
        a (str): 第一个函数的代码
        b (str): 第二个函数的代码
        threshold (float): 相似度阈值，默认为0.9
        
    Returns:
        bool: 如果函数相似度超过阈值则返回True，否则返回False
    """
    # 首先去除两个函数中的注释
    a_clean = remove_comments_from_string(a)
    b_clean = remove_comments_from_string(b)
    return SequenceMatcher(None, a_clean, b_clean).ratio() > threshold

def process_json_file(file_path: Path, threshold: float = 0.9, dry_run: bool = False) -> Tuple[int, int]:
    """
    处理单个JSON文件，去除注释并去重
    
    Args:
        file_path (Path): JSON文件路径
        threshold (float): 函数相似度阈值
        dry_run (bool): 是否为预览模式
        
    Returns:
        Tuple[int, int]: (原始函数数量, 去重后函数数量)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError(f"文件 {file_path} 的内容不是列表格式")

        # 用于存储唯一的函数对
        unique_pairs = []
        
        print(f"\n处理文件: {file_path}")
        for item in tqdm(data, desc="处理函数"):
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
            output_dir = file_path.parent / 'processed'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存处理后的文件
            output_file = output_dir / file_path.name
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(unique_pairs, f, indent=2, ensure_ascii=False)
            
            print(f"处理完成:")
            print(f"原始函数数量: {len(data)}")
            print(f"去重后函数数量: {len(unique_pairs)}")
            print(f"输出文件保存至: {output_file}")
        else:
            print(f"预览模式:")
            print(f"原始函数数量: {len(data)}")
            print(f"去重后函数数量: {len(unique_pairs)}")
            
        return len(data), len(unique_pairs)
            
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        return 0, 0

def process_directory(
    directory: str,
    threshold: float = 0.9,
    dry_run: bool = False,
    pattern: str = "*.json"
) -> ProcessingStats:
    """
    处理目录中的所有JSON文件，去除注释并去重
    
    Args:
        directory (str | Path): 要处理的目录路径
        threshold (float): 函数相似度阈值，默认为0.9
        dry_run (bool): 是否为预览模式，默认为False
        pattern (str): 文件匹配模式，默认为"*.json"
        
    Returns:
        ProcessingStats: 处理统计信息
        
    Raises:
        FileNotFoundError: 如果目录不存在
    """
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")
    
    stats = ProcessingStats()
    
    # 获取所有匹配的文件
    json_files = list(directory.rglob(pattern))
    stats.total_files = len(json_files)
    
    # 处理每个文件
    for file_path in tqdm(json_files, desc="处理文件"):
        try:
            total_funcs, unique_funcs = process_json_file(file_path, threshold, dry_run)
            if total_funcs > 0:
                stats.processed_files += 1
                stats.total_functions += total_funcs
                stats.unique_functions += unique_funcs
            else:
                stats.failed_files += 1
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            stats.failed_files += 1
    
    # 打印总体统计信息
    print("\n处理完成！总体统计：")
    print(f"处理的文件总数: {stats.total_files}")
    print(f"成功处理文件数: {stats.processed_files}")
    print(f"处理失败文件数: {stats.failed_files}")
    print(f"处理的函数总数: {stats.total_functions}")
    print(f"去重后函数总数: {stats.unique_functions}")
    print(f"重复函数数量: {stats.total_functions - stats.unique_functions}")
    
    return stats

def main():
    parser = argparse.ArgumentParser(description='处理JSON文件中的函数：去除注释并去重')
    parser.add_argument('directory', help='包含JSON文件的目录路径')
    parser.add_argument('--threshold', type=float, default=0.9, 
                      help='函数相似度阈值 (0.0-1.0), 默认为0.9')
    parser.add_argument('--dry-run', action='store_true', 
                      help='预览模式，不实际修改文件')
    parser.add_argument('--pattern', type=str, default='*.json',
                      help='文件匹配模式，默认为"*.json"')
    
    args = parser.parse_args()
    
    try:
        process_directory(args.directory, args.threshold, args.dry_run, args.pattern)
    except Exception as e:
        print(f"错误：{e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 