# -*- coding: utf-8 -*-
import os
import re
import json
from typing import Dict, List, Tuple

class CodeBlockProcessor:
    def __init__(self):
        # 定义核心正则表达式模式
        self.patterns = {
            "fim_candidate": re.compile(
                r'(?P<above>.*?\{)\s*'  # 前文（到代码块开始）
                r'(?P<target>.*?)(?=\n\s*\S)'  # 待补全目标（非空白行开始前）
                r'(?P<follow>.*?\})',  # 后文
                re.DOTALL
            ),
            "function_block": re.compile(
                r'function\s+\w+.*?\{.*?\n\}',
                re.DOTALL
            ),
            "import_statement": re.compile(
                r'import\s+.*?from\s+[\'"][^\'"]+[\'"];',
                re.MULTILINE
            ),
            "test_case": re.compile(
                r'it\(.*?,\s*\d+,\s*\(\)\s*=>\s*\{.*?\n\s*\}\)',
                re.DOTALL
            )
        }

    def split_code_block(self, code: str) -> List[Dict]:
        """分割代码块为FIM任务片段"""
        candidates = []

        # 按函数块处理
        for func_match in self.patterns["function_block"].finditer(code):
            func_code = func_match.group()
            if fim_match := self.patterns["fim_candidate"].search(func_code):
                candidates.append({
                    "above": fim_match.group("above").strip(),
                    "target": fim_match.group("target").strip(),
                    "follow": fim_match.group("follow").strip()
                })

        # 按测试用例处理
        for test_match in self.patterns["test_case"].finditer(code):
            test_code = test_match.group()
            lines = test_code.split('\n')
            if len(lines) > 3:
                split_point = len(lines) // 2
                candidates.append({
                    "above": '\n'.join(lines[:split_point]),
                    "target": '\n'.join(lines[split_point:]),
                    "follow": ""
                })

        return candidates

    def split_ui_code_block(self, code: str) -> List[Dict]:
        """Split ui_code block into FIM task fragments."""
        candidates = []

        # Match `build()` function and its nested structure
        build_pattern = re.compile(
            r'(?P<above>.*?build\(\)\s*\{)'  # Match the `build()` function header
            r'(?P<target>.*?)'  # Match the content inside `build()`
            r'(?P<follow>\})',  # Match the closing brace of `build()`
            re.DOTALL
        )

        # Process `build()` function
        if build_match := build_pattern.search(code):
            candidates.append({
                "above": build_match.group("above").strip(),
                "target": build_match.group("target").strip(),
                "follow": build_match.group("follow").strip()
            })

        return candidates

    def generate_fim_records(self, code_data: Dict) -> List[Dict]:
        """Generate FIM format records with original code included."""
        records = []

        # Process function content
        for func in code_data["functions"]:
            if "content" in func:
                for snippet in self.split_code_block(func["content"]):
                    record = {
                        "id": func.get("id", ""),  # Use function ID if available
                        "url": code_data.get("repo_url", ""),
                        "file_path": code_data["file"],
                        "xl_context": self._get_xl_context(code_data),
                        "above_context_without_fim_start": snippet["above"],
                        "follow_context_without_fim_end": snippet["follow"],
                        "fim_task_sector_start": "",  # Customize as needed
                        "fim_task_sector_end": "",  # Customize as needed
                        "fim_target": snippet["target"],
                        "original_code": func["content"]  # Save the original code
                    }
                    records.append(record)

        # Process ui_code content
        for ui in code_data["ui_code"]:
            if "content" in ui:
                for snippet in self.split_ui_code_block(ui["content"]):  # Use the new method
                    record = {
                        "id": ui.get("id", ""),  # Use ui_code ID if available
                        "url": code_data.get("repo_url", ""),
                        "file_path": code_data["file"],
                        "xl_context": self._get_xl_context(code_data),
                        "above_context_without_fim_start": snippet["above"],
                        "follow_context_without_fim_end": snippet["follow"],
                        "fim_task_sector_start": "",  # Customize as needed
                        "fim_task_sector_end": "",  # Customize as needed
                        "fim_target": snippet["target"],
                        "original_code": ui["content"]  # Save the original code
                    }
                    records.append(record)

        return records

    def _get_xl_context(self, code_data: Dict) -> List[str]:
        """提取跨文件上下文"""
        context = []

        # 提取导入信息
        for imp in code_data.get("imports", []):
            if "full_import" in imp:
                context.append(imp["full_import"])

        # 提取关联函数签名
        for func in code_data.get("functions", []):
            if "name" in func and "params" in func:
                context.append(f"function {func['name']}({', '.join(func['params'])})")

        return context

    def process_folder(self, folder_path: str, output_folder: str) -> None:
        """Process all JSON files in a folder and save the output to a corresponding file in the output folder."""
        os.makedirs(output_folder, exist_ok=True)  # Ensure the output folder exists

        for file_name in os.listdir(folder_path):
            if file_name.endswith('.json'):
                input_file_path = os.path.join(folder_path, file_name)
                output_file_path = os.path.join(output_folder, file_name)  # Use the same file name in the output folder

                with open(input_file_path, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)  # Each file contains a list of data structures
                    all_records = []
                    for data in data_list:
                        records = self.generate_fim_records(data)
                        all_records.extend(records)

                # Save the results to the corresponding output file
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    json.dump(all_records, output_file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    folder_path = "E:\\HMOutput"  # Input folder path
    output_folder = "E:\\ProcessedOutput"  # Output folder path
    processor = CodeBlockProcessor()
    processor.process_folder(folder_path, output_folder)
    print(f"Processing completed. Results saved to {output_folder}")