import os
import re
import json

from ArkTSAbstractor.importAnalyzer import analyze_imports
from ArkTSAbstractor.logger import setup_logger, log_directory
from tool import load_reserved_words

function_folder = './complete_function'

reserved_words = load_reserved_words()
logger = setup_logger('file_analyzer_logger', os.path.join(log_directory, 'file_analyzer.log'))

class ETSFileAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_type = None
        self.ui_code = []
        self.variables = []
        self.functions = []
        self.imports = []

    def set_file_type(self, file_type):
        self.file_type = file_type

    def add_ui_code(self, ui_code):
        self.ui_code.append(ui_code)

    def add_variable(self, variable):
        self.variables.append(variable)

    def add_function(self, function):
        self.functions.append(function)

    def add_reference(self, import_type, module_name, full_import, component_name=None, alias=None):
        reference = {
            'import_type': import_type,
            'module_name': module_name,
            'full_import': full_import,
            'component_name': component_name,
            'alias': alias
        }
        self.imports.append(reference)

def find_balanced_braces(content, start_pos):
    brace_count = 0
    for i in range(start_pos, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
        if brace_count == 0:
            return i
    return -1

def analyze_ets_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            file_contents = file.read()
            file_basename = os.path.basename(file_path)
            analysis = ETSFileAnalysis(file_contents)
            references = analyze_imports(file_contents)
            analysis.imports = references.references
            complete_functions = []
            # Determine file type
            if re.search(r'@Entry\s*@Component\s*struct', file_contents):
                analysis.set_file_type("Page")
            elif re.search(r'@Component\s*(export)?\s*struct', file_contents):
                analysis.set_file_type("Component")
            else:
                analysis.set_file_type("Service")

            # Extract UI code blocks
            ui_code_patterns = [r'build\s*\(\)\s*\{', r'@Builder\s*\w+\s?\((\w+\s?:+\s?\w+)?\)\s*\{']
            matches = []

            # 收集所有匹配项及其对应的起始和结束位置
            for pattern in ui_code_patterns:
                for match in re.finditer(pattern, file_contents):
                    match_start = match.start()
                    start_pos = match.end() - 1
                    end_pos = find_balanced_braces(file_contents, start_pos)
                    if end_pos != -1:
                        # 提取并保存UI代码到分析对象
                        ui_code = file_contents[match_start:end_pos + 1].strip()
                        analysis.add_ui_code(ui_code)
                        # 记录需要删除的区间（起始和结束位置）
                        matches.append((match_start, end_pos + 1))

            # 按起始位置逆序排序，确保从后往前处理
            matches.sort(reverse=True, key=lambda x: x[0])

            # 从文件内容中删除所有记录的UI代码块
            for start, end in matches:
                file_contents = file_contents[:start] + file_contents[end:]

            # Extract variable declarations
            variable_pattern = re.compile(
                r'(@\w+\s)?((private|public)\s)?((static)\s)?((const|let|val|var)\s)?(\w+)\s?:\s?([^=\s]+)(\s?=\s?([^;\n{]+))?;?\n')
            for match in variable_pattern.finditer(file_contents):
                if match.group(8) in reserved_words:
                    # 记录这个错误到文件
                    # logger.error("Reserved word used as variable name: " + match.group(8) + " in file: " + analysis.file_path)
                    continue
                variable = {
                    'modifier': match.group(1).strip() if match.group(1) else None,
                    'name': match.group(8).strip(),
                    'type': match.group(9).strip(),
                    'value': match.group(11).strip() if match.group(11) else None
                }
                analysis.add_variable(variable)

            # Extract function declarations, ignoring build() and @Builder functions
            # function_pattern = re.compile(r'(\w+\s+)?(\w+)\s*\([^)]*\)\s*\{')
            function_pattern = re.compile(
                r'(\w+\s)?(\w+\s?)(=\s?)?\(\s?((\.\.\.)?((\w+\??\s?:\s?[^)]+\s?)(,\s?\w+\??\s?:\s?[^)]+)*)?)\)\s*?\s?(=>\s?)?(:\s?\w+\s?)?\{')
            for match in function_pattern.finditer(file_contents):
                function_name = match.group(2).strip() if match.group(2) else None
                if function_name in reserved_words:
                    # 记录这个错误到文件
                    # logger.error("Reserved word used as function name: " + function_name + " in file: " + analysis.file_path)
                    continue
                if function_name != 'build':
                    start_pos = match.end() - 1
                    end_pos = find_balanced_braces(file_contents, start_pos)
                    if match.group(1) and match.group(1).strip() == 'Builder':
                        continue
                    if end_pos != -1:
                        if function_name and file_contents[start_pos:end_pos + 1].strip():
                            function = {
                                'modifier': match.group(1).strip() if match.group(1) else None,
                                'name': function_name,
                                'body': file_contents[start_pos:end_pos + 1].strip()
                            }
                            analysis.add_function(function)
                        if file_contents[match.start():end_pos + 1].strip():
                            complete_functions.append((references.references, file_contents[match.start():end_pos + 1].strip()))
            if not os.path.exists(function_folder):
                os.makedirs(function_folder)
            if complete_functions:
                file_path = os.path.join(function_folder, file_basename + '.json')
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_functions = json.load(f)
                    complete_functions.extend(existing_functions)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(complete_functions, f, indent=4, ensure_ascii=False)

            return analysis
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")




