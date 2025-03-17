import os
import json
from tqdm import tqdm
import argparse
from pathlib import Path
from typing import Dict, List, Optional

class CodeClassifier:
    def __init__(self, base_output_dir: Path):
        self.output_dirs = {
            'test_ui': base_output_dir / 'code_classification/test_UI',
            'test_function': base_output_dir / 'code_classification/test_function',
            'ui': base_output_dir / 'code_classification/UI',
            'function': base_output_dir / 'code_classification/function'
        }
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'error_files': 0,
            'classified_codes': {
                'test_ui': 0,
                'test_function': 0,
                'ui': 0,
                'function': 0
            }
        }

    def ensure_output_dirs(self):
        """确保所有输出目录存在"""
        for dir_path in self.output_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

    def save_codes(self, codes: List[str], category: str, filename: str) -> bool:
        """保存代码到指定类别的文件中"""
        if not codes:
            return False

        try:
            output_file = self.output_dirs[category] / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(codes, f, indent=4, ensure_ascii=False)
            self.stats['classified_codes'][category] += len(codes)
            return True
        except Exception as e:
            print(f"保存{category}类别的文件 {filename} 时出错: {e}")
            return False

    def process_file(self, file_path: Path) -> bool:
        """处理单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            codes = {
                'test_ui': [],
                'test_function': [],
                'ui': [],
                'function': []
            }

            for item in data:
                if 'file' not in item:
                    continue

                is_test = 'test' in item['file'].lower()
                
                if 'ui_code' in item and item['ui_code']:
                    target = 'test_ui' if is_test else 'ui'
                    codes[target].extend(item['ui_code'])
                
                if 'functions' in item and item['functions']:
                    target = 'test_function' if is_test else 'function'
                    codes[target].extend(item['functions'])

            # 保存分类后的代码
            filename = file_path.name
            success = False
            for category, code_list in codes.items():
                if self.save_codes(code_list, category, filename):
                    success = True

            if success:
                self.stats['processed_files'] += 1
            return success

        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            self.stats['error_files'] += 1
            return False

    def classify_code(self, folder_path: Path):
        """分类指定文件夹中的代码"""
        if not folder_path.exists():
            raise FileNotFoundError(f"目录不存在: {folder_path}")

        self.ensure_output_dirs()
        json_files = list(folder_path.glob('*.json'))
        self.stats['total_files'] = len(json_files)

        for file_path in tqdm(json_files, desc="正在处理文件"):
            self.process_file(file_path)

        self._print_statistics()

    def _print_statistics(self):
        """打印处理统计信息"""
        print("\n处理完成！统计信息：")
        print(f"总文件数: {self.stats['total_files']}")
        print(f"成功处理: {self.stats['processed_files']}")
        print(f"处理失败: {self.stats['error_files']}")
        print("\n代码分类统计：")
        for category, count in self.stats['classified_codes'].items():
            print(f"{category}: {count} 个代码片段")

def main():
    parser = argparse.ArgumentParser(description='代码分类工具')
    parser.add_argument('input_dir', type=str, help='输入目录路径，包含要分类的JSON文件')
    parser.add_argument('--output-dir', type=str, default='.', 
                      help='输出根目录路径（默认为当前目录）')

    args = parser.parse_args()
    
    try:
        input_path = Path(args.input_dir)
        output_path = Path(args.output_dir)
        
        classifier = CodeClassifier(output_path)
        classifier.classify_code(input_path)
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

