import re
import random
from typing import Dict, Optional, Tuple
import ast



def split_arkts_code(code: str) -> Optional[Dict[str, str]]:
    """保证fim_target非空的分割函数"""

    patterns = {
        'build': re.compile(
            r'(\bbuild\s*\(\)\s*\{)(.*?)(^\}\s*$)',
            re.DOTALL | re.MULTILINE
        ),
        'generic': re.compile(
            r'((?:const|let|function)?\s*\w+\s*=\s*\(.*?\)\s*:?\s*\w*\s*=>\s*\{)(.*?)(^\}\s*,?\s*$)',
            re.DOTALL | re.MULTILINE
        )
    }

    match = patterns['build'].search(code)
    func_type = 'build'
    if not match:
        match = patterns['generic'].search(code)
        func_type = 'generic'
        if not match:
            return None

    func_head = match.group(1).rstrip()
    func_body = match.group(2)
    func_tail = match.group(3).strip()

    # 保证至少有一个有效分割点
    for _ in range(3):  # 最多尝试3次
        split_line, split_pos = find_random_split_point(func_body, func_type)
        body_before, body_after = split_body(func_body, split_line, split_pos)

        # 有效性校验
        if len(body_after.strip()) > 0:
            break
    else:  # 所有尝试都失败时使用保底策略
        split_line = max(len(func_body.split('\n')) // 2, 1)
        body_before, body_after = split_body(func_body, split_line, 0)
        body_after = body_after or func_body[-10:]  # 截取最后10个字符作为保底

    return {
        'fim_target': body_after,
        'fim_task_sector_start': f"{func_head}{body_before}",
        'fim_task_sector_end': f"{func_tail}",
        'above_context_without_fim_start': code[:match.start()].strip(),
        'follow_context_without_fim_end': code[match.end():].strip(),
        'function_type': func_type
    }


def find_random_split_point(body: str, func_type: str) -> Tuple[int, int]:
    """增强型随机分割点查找"""
    lines = [line for line in body.split('\n') if line.strip()]
    if not lines:
        return 0, 0

    # 排除最后一行避免空target
    max_line = len(lines) - 1 if len(lines) > 1 else 0
    line_num = random.randint(0, max_line)

    current_line = lines[line_num]
    candidates = []

    # 收集有效分割点（排除行首和行尾）
    for match in re.finditer(r'\S+', current_line):
        if 0 < match.end() < len(current_line):
            candidates.append(match.end())

    # 保底选择行中间
    split_pos = random.choice(candidates) if candidates else len(current_line) // 2

    return line_num, split_pos


def split_body(body: str, split_line: int, split_pos: int) -> Tuple[str, str]:
    """安全分割函数体"""
    lines = body.split('\n')

    try:
        current_line = lines[split_line]
    except IndexError:
        return (body, "")

    # 确保分割后内容不为空
    if split_pos >= len(current_line.rstrip()):
        split_line = max(split_line - 1, 0)
        current_line = lines[split_line]
        split_pos = len(current_line) // 2

    before = '\n'.join(lines[:split_line] + [current_line[:split_pos].rstrip()])
    after = '\n'.join([current_line[split_pos:].lstrip()] + lines[split_line + 1:])

    return (before, after)


def validate_reconstruction(original: str, parts: Dict[str, str]) -> bool:
    """验证代码重组是否与原始代码一致"""
    try:
        # 拼接逻辑（关键步骤）
        reconstructed = (
                parts['above_context_without_fim_start'] +
                parts['fim_task_sector_start'] +
                parts['fim_target'] +
                parts['fim_task_sector_end'].split('}')[0] +  # 移除可能重复的闭合括号
                '}' +  # 添加统一闭合
                parts['follow_context_without_fim_end']
        )

        # 标准化对比（处理空白差异）
        def normalize_code(s):
            return re.sub(r'\s+', '', s.translate(str.maketrans('', '', '\'"`')))

        return normalize_code(original) == normalize_code(reconstructed)
    except Exception as e:
        print(f"Validation failed: {str(e)}")
        return False
import json

def read_pre_from_json(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            pre_parts = []
            for item in data:
                if "pre" in item:
                    try:
                        # 使用 ast.literal_eval 转换转义符号
                        processed_pre = ast.literal_eval('"' + item["pre"] + '"')
                        pre_parts.append(processed_pre)
                    except SyntaxError:
                        print(f"处理 {item['pre']} 时发生语法错误，跳过此条数据。")
                        continue
            return pre_parts
    except FileNotFoundError:
        print(f"未找到文件: {json_file_path}")
    except json.JSONDecodeError:
        print(f"解析JSON文件 {json_file_path} 时出错，请检查文件格式。")
    except Exception as e:
        print(f"处理文件 {json_file_path} 时发生未知错误: {e}")

def process_test_cases(test_cases):
    results = {}
    for idx, code in enumerate(test_cases, 1):
        print(f"\n=== Testing Case {idx} ===")
        original = code.strip()
        result = split_arkts_code(original)

        if not result:
            print("No valid function found")
            continue

        # 执行验证
        is_valid = validate_reconstruction(original, result)

        print("[Validation Result]", "PASS" if is_valid else "FAIL")
        print("\nOriginal Code:\n" + original)
        print("\nReconstructed Code:\n" + (
                result['above_context_without_fim_start'] +
                result['fim_task_sector_start'] +
                result['fim_target'] +
                result['fim_task_sector_end'].split('}')[0] + '}' +
                result['follow_context_without_fim_end']
        ))
        results[idx] = result
    return results

import os
import json

def process_json_files(input_folder: str, output_folder: str) -> None:
    """Process all JSON files in a folder and save the results to another folder."""
    os.makedirs(output_folder, exist_ok=True)  # Ensure the output folder exists

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.json'):
            input_file_path = os.path.join(input_folder, file_name)
            output_file_path = os.path.join(output_folder, file_name)  # Use the same file name in the output folder

            with open(input_file_path, 'r', encoding='utf-8') as input_file:
                data = json.load(input_file)  # Load JSON data
                processed_data = process_data(data)  # Process the data (customize this function)

            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                json.dump(processed_data, output_file, indent=2, ensure_ascii=False)  # Save processed data

def process_data(data):
    """Custom data processing logic."""
    # Example: Return the data as-is without modification

    return process_test_cases(test_cases)

if __name__ == "__main__":
    input_folder = r"E:\HMOutput"  # Replace with your input folder path
    output_folder = r"E:\ProcessedOutput"  # Replace with your output folder path
    process_json_files(input_folder, output_folder)
    print(f"Processing completed. Results saved to {output_folder}")
# if __name__ == "__main__":
#
#     test_cases = read_pre_from_json("/Users/liuxuejin/Desktop/Projects/PythonTools/output/extracted_pre_tags_with_instructions.json")
#     all_results = process_test_cases(test_cases)
#     # 你可以在这里添加保存结果的逻辑，例如保存到JSON文件
#     import json
#     with open('code_split_results.json', 'w', encoding='utf-8') as f:
#         json.dump(all_results, f, ensure_ascii=False, indent=4)