import os
import json
import re
from tqdm import tqdm
import argparse
from pathlib import Path

def process_json_file(file_path, output_dir=None, origin_only=True):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"文件 {file_path} 的内容不是列表格式")

        updated_data = []

        for item in data:
            if not isinstance(item, list) or len(item) != 2:
                print(f"警告: 跳过无效数据项 {item}")
                continue

            imports, code_str = item

            if origin_only:
                all_imports_valid = all(imp['module_name'].startswith('@') for imp in imports)
                if not all_imports_valid:
                    continue

            full_imports = []

            for imp in imports:
                component_name = imp['component_name']
                alias = imp['alias']
                search_term = alias if alias else component_name

                if re.search(r'\b' + re.escape(search_term) + r'\b', code_str):
                    full_imports.append(imp['full_import'])

            if full_imports:
                code_str = '\n'.join(full_imports) + '\n' + code_str

            # for variable in item['variables']:

            if code_str.strip():
                updated_data.append(code_str)

        if updated_data:
            if output_dir is None:
                output_dir = Path(file_path).parent / ('processed_ORIGIN_ONLY' if origin_only else 'processed')
            else:
                output_dir = Path(output_dir)
            
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / Path(file_path).name

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)

            print(f"处理后的文件已保存到: {output_file}")
            return True

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        return False

def process_directory(directory, output_dir=None, origin_only=True):
    directory = Path(directory)
    if not directory.exists():
        print(f"错误: 目录 '{directory}' 不存在")
        return

    success_count = 0
    total_files = 0

    for file_path in tqdm(list(directory.rglob('*.json'))):
        total_files += 1
        if process_json_file(file_path, output_dir, origin_only):
            success_count += 1

    print(f"\n处理完成! 成功处理 {success_count}/{total_files} 个文件")

def main():
    parser = argparse.ArgumentParser(description='处理JSON文件并添加导入语句')
    parser.add_argument('input_dir', type=str, help='输入目录路径')
    parser.add_argument('--output-dir', type=str, help='输出目录路径（可选）')
    parser.add_argument('--process-all', action='store_false', dest='origin_only',
                      help='处理所有文件（默认只处理原始文件）')

    args = parser.parse_args()
    process_directory(args.input_dir, args.output_dir, args.origin_only)

if __name__ == "__main__":
    # main()
    process_directory('/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/data/processed_ui_with_import', '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/data/processed_ui_with_import_added_import', True)