import re
import random
from typing import Dict, Tuple


def split_arkts_code(code: str) -> Dict[str, str]:
    """保证fim_target非空的分割函数，添加默认分割保证所有代码都能被处理"""
    patterns = {
        'build': re.compile(
            r'(\bbuild\s*\(\)\s*\{)(.*?)(^\}\s*$)',
            re.DOTALL | re.MULTILINE
        ),
        'function': re.compile(  # 匹配常规函数声明
            r'(function\s+\w+\s*\(.*?\)\s*\{)(.*?)(^\}\s*$)',
            re.DOTALL | re.MULTILINE
        ),
        'arrow_func': re.compile(  # 匹配箭头函数
            r'((?:const|let|var)\s+\w+\s*=\s*(?:\([^)]*\)|[^=]*?)\s*:?\s*\w*\s*=>\s*\{)(.*?)(^\}[,;]?\s*$)',
            re.DOTALL | re.MULTILINE
        ),
        'try_catch': re.compile(  # 匹配try-catch结构
            r'(\btry\s*\{)(.*?)(^\}\s*catch\s*\([^)]*\)\s*\{[^}]*\}\s*)',
            re.DOTALL | re.MULTILINE
        )
    }

    # 按优先级尝试匹配不同模式
    for func_type, pattern in patterns.items():
        match = pattern.search(code)
        if match:
            break
    else:  # 无匹配时使用默认分割
        return default_split(code)

    # 提取匹配组
    func_head = match.group(1).rstrip()
    func_body = match.group(2)
    func_tail = match.group(3).strip()

    # 在函数体内寻找有效分割点
    for _ in range(3):
        split_line, split_pos = find_random_split_point(func_body, func_type)
        body_before, body_after = split_body(func_body, split_line, split_pos)
        if body_after.strip():
            break
    else:  # 保底策略
        body_before, body_after = func_body[:-10], func_body[-10:]

    return {
        'fim_target': body_after,
        'fim_task_sector_start': f"{func_head}{body_before}",
        'fim_task_sector_end': f"{func_tail}",
        'above_context_without_fim_start': code[:match.start()].strip(),
        'follow_context_without_fim_end': code[match.end():].strip(),
        'function_type': func_type
    }


def default_split(code: str) -> Dict[str, str]:
    """优化的默认分割策略"""
    if not code.strip():
        return {
            'fim_target': '',
            'fim_task_sector_start': '',
            'fim_task_sector_end': '',
            'above_context_without_fim_start': '',
            'follow_context_without_fim_end': '',
            'function_type': 'default'
        }

    lines = code.splitlines()
    if not lines:
        return {
            'fim_target': '',
            'fim_task_sector_start': '',
            'fim_task_sector_end': '',
            'above_context_without_fim_start': '',
            'follow_context_without_fim_end': '',
            'function_type': 'default'
        }

    # 寻找语义分割点（空行/块结束符）
    split_point = next((
        i for i, line in enumerate(lines[1:], start=1)
        if not line.strip()
           or line.strip().endswith((';', '}'))
    ), len(lines) // 2)

    # 确保非空分割
    before = "\n".join(lines[:split_point])
    after = "\n".join(lines[split_point:])

    if not before.strip():
        before = lines[0]
        after = "\n".join(lines[1:])
    elif not after.strip():
        before = "\n".join(lines[:-1])
        after = lines[-1]

    return {
        'fim_target': after,
        'fim_task_sector_start': before,
        'fim_task_sector_end': '}',
        'above_context_without_fim_start': '',
        'follow_context_without_fim_end': '',
        'function_type': 'default'
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

    if not lines:
        return ("", "")

    # 确保split_line在有效范围内
    split_line = max(0, min(split_line, len(lines) - 1))

    current_line = lines[split_line]

    # 确保分割点有效
    split_pos = max(0, min(split_pos, len(current_line)))

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
    """处理从JSON文件加载的数据，提取代码片段并进行分割处理。"""
    code_samples = []
    for item in data:
        if "pre" in item:
            try:
                # 使用 ast.literal_eval 转换转义符号
                processed_pre = ast.literal_eval('"' + item["pre"] + '"')
                code_samples.append(processed_pre)
            except SyntaxError:
                print(f"处理 {item['pre']} 时发生语法错误，跳过此条数据。")
                continue
            except Exception as e:
                print(f"处理数据时发生错误: {e}")
                continue

    # 处理提取的代码样本
    return process_test_cases(code_samples)


import os
import json
import random
import re
import ast
from typing import Dict, Tuple, List, Any
from codeTemplate import get_ui_code, get_fx_code
# 处理ProjectAbstractor生成的结果文件，为functions和ui_code生成完整代码并分割
def process_abstracted_json(input_folder: str, output_folder: str, force_reprocess=False) -> None:
    """处理ProjectAbstractor生成的结果文件，为functions和ui_code生成完整代码并分割"""
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取所有JSON文件
    json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    skipped_count = 0
    processed_count = 0
    error_count = 0
    processed_items_count = 0  # 记录成功处理的代码段数量

    function_count = 0
    ui_code_count = 0
    default_split_count = 0

    for json_file in json_files:
        input_path = os.path.join(input_folder, json_file)
        output_path = os.path.join(output_folder, json_file)

        # 检查文件是否已处理
        if os.path.exists(output_path) and not force_reprocess:
            print(f"跳过已处理文件: {json_file}")
            skipped_count += 1
            continue

        # 处理当前文件
        print(f"处理文件: {json_file}")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            processed_results = []

            # 遍历每个文件项
            for file_item in data:
                file_name = os.path.basename(file_item.get("file", "unknown_file")).split('.')[0]
                file_path = file_item.get("file", "")

                # 处理functions
                for function in file_item.get("functions", []):
                    try:
                        function_id = function.get("id", "")
                        function_name = function.get("name", "")
                        function_content = function.get("content", "")

                        if not function_content:
                            continue

                        # 构造数据对象
                        function_data = {
                            'import': [],
                            'variables': [],
                            'content': function_content
                        }

                        # 获取依赖信息
                        dependencies = function.get("dependencies", {})
                        imports = dependencies.get("imports", [])
                        if imports:
                            function_data['import'] = imports

                        # 生成完整代码
                        try:
                            xl_context, full_code = get_fx_code(function_data, file_name=file_name)
                        except Exception as e:
                            # 如果使用模板生成失败，直接使用原始内容
                            xl_context = []
                            full_code = function_content
                            print(f"  - 生成函数代码失败: {str(e)[:100]}...")

                        # 分割代码
                        split_result = split_arkts_code(full_code)

                        if split_result['function_type'] == 'default':
                            default_split_count += 1
                        function_count += 1

                        # 由于split_arkts_code总是返回结果，不需要再检查split_result是否为None
                        processed_results.append({
                            "id": function_id,
                            "name": function_name,
                            "file": file_path,
                            "original_content": function_content,
                            "xl_context": xl_context,
                            "full_code": full_code,
                            "split_result": split_result,
                            "type": "function"
                        })
                        processed_items_count += 1
                    except Exception as e:
                        print(f"  - 处理函数时出错: {str(e)}")
                        continue

                # 处理UI代码
                for ui_code in file_item.get("ui_code", []):
                    try:
                        ui_id = ui_code.get("id", "")
                        ui_name = ui_code.get("name", "")
                        ui_content = ui_code.get("content", "")

                        if not ui_content:
                            continue

                        # 构造数据对象
                        ui_data = {
                            'import': [],
                            'variables': [],
                            'content': ui_content
                        }

                        # 获取依赖信息
                        dependencies = ui_code.get("dependencies", {})
                        imports = dependencies.get("imports", [])
                        if imports:
                            ui_data['import'] = imports

                        # 生成完整代码
                        try:
                            xl_context, full_code = get_ui_code(ui_data, file_name=file_name)
                        except Exception as e:
                            # 如果使用模板生成失败，直接使用原始内容
                            xl_context = []
                            full_code = ui_content
                            print(f"  - 生成UI代码失败: {str(e)[:100]}...")

                        # 分割代码 - 现在总是会返回结果
                        split_result = split_arkts_code(full_code)
                        
                        ui_code_count += 1

                        # 由于split_arkts_code总是返回结果，不需要再检查split_result是否为None
                        processed_results.append({
                            "id": ui_id,
                            "name": ui_name,
                            "file": file_path,
                            "original_content": ui_content,
                            "xl_context": xl_context,
                            "full_code": full_code,
                            "split_result": split_result,
                            "type": "ui_code"
                        })
                        processed_items_count += 1
                    except Exception as e:
                        print(f"  - 处理UI代码时出错: {str(e)}")
                        continue

            # 保存处理结果
            if processed_results:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(processed_results, f, ensure_ascii=False, indent=2)
                processed_count += 1
            else:
                print(f"  - 没有找到可处理的代码片段")
                error_count += 1

        except Exception as e:
            print(f"处理文件 {json_file} 时出错: {str(e)}")
            error_count += 1

    print(f"所有文件处理完成，共处理 {processed_count} 个文件，跳过 {skipped_count} 个文件，失败 {error_count} 个文件")
    print(f"成功处理 {processed_items_count} 个代码段（包括函数和UI组件）")
    print(f"结果已保存到 {output_folder}")
    print(f"处理完成，共处理 {processed_count} 个JSON文件")
    print(f"函数总条数: {function_count} UI代码总条数: {ui_code_count}")
    print(f"使用默认分割方式的条数: {default_split_count}")
import codecs
def process_docs_json(input_file:str, output_file:str):
    """处理ProjectAbstractor生成的结果文件，为functions和ui_code生成完整代码并分割"""
    skipped_count = 0
    processed_count = 0
    error_count = 0
    processed_items_count = 0  # 记录成功处理的代码段数量
    default_split_count = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        datas = json.load(f)
        processed_results = []
            # 分割代码
        for data in datas:
            if data.get('type', '') == 'Import':
                continue
            if 'pre' in data and isinstance(data['pre'], str):
                try:
                    data['pre'] = codecs.decode(data['pre'], 'unicode_escape')
                except Exception as e:
                    # 如果上面的方法失败，尝试直接替换
                    data['pre'] = data['pre'].replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')

            full_code = data.get('pre', '')
            split_result = split_arkts_code(full_code)

            # 由于split_arkts_code总是返回结果，不需要再检查split_result是否为None
            processed_results.append({
                "id": data.get('id', 0),
                "name": data.get('function_name', ""),
                "file": data.get('file_path', ""),
                "original_content": full_code,
                "xl_context": [],
                "full_code": full_code,
                "split_result": split_result,
                "type": "Reference"
            })
            processed_items_count += 1
            if split_result['function_type'] == 'default':
                default_split_count += 1
            # 保存处理结果
        if processed_results:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_results, f, ensure_ascii=False, indent=2)
        else:
            print(f"  - 没有找到可处理的代码片段")

    print(f"所有文件处理完成，共处理 {processed_count} 个文件，跳过 {skipped_count} 个文件，失败 {error_count} 个文件")
    print(f"成功处理 {processed_items_count} 个代码段（包括函数和UI组件）")
    print(f"处理完成，共处理 {processed_count} 个JSON文件")
    print(f"使用默认分割方式的条数: {default_split_count}")
# 下面可以添加主函数调用
# if __name__ == "__main__":
#     input_folder = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/projects_abstracted"
#     output_folder = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/projects_split"
#
#     process_abstracted_json(input_folder, output_folder, force_reprocess=False)

if __name__ == '__main__':
    input_file = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSRetrival/data/extracted_harmonyos-references.json"
    output_file = "/Volumes/P800/docsCode/processed_harmonyos_references.json"
    process_docs_json(input_file, output_file)