import os
import re
import json

from ArkTSAbstractor.importAnalyzer import analyze_imports
from ArkTSAbstractor.logger import setup_logger, log_directory
from tool import load_reserved_words

function_folder = './complete_function'
ui_folder = './ui_with_import'

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
            
            # 优化导入语句
            optimized_imports = []
            for ref in references.references:
                if ref['import_type'] == 'named' and ',' in ref['component_name']:
                    # 处理多个命名导入的情况
                    module_name = ref['module_name']
                    components = [c.strip() for c in ref['component_name'].split(',')]
                    for component in components:
                        optimized_imports.append({
                            'import_type': 'named',
                            'module_name': module_name,
                            'full_import': f"import {{ {component} }} from '{module_name}';",
                            'component_name': component,
                            'alias': None
                        })
                elif ref['import_type'] == 'default' and '{' in ref['component_name']:
                    # 处理默认导入和命名导入混合的情况
                    module_name = ref['module_name']
                    # 分离默认导入和命名导入
                    parts = ref['component_name'].split(',')
                    default_import = parts[0].strip()
                    named_imports = parts[1].strip('{} ').split(',')
                    
                    # 添加默认导入
                    optimized_imports.append({
                        'import_type': 'default',
                        'module_name': module_name,
                        'full_import': f"import {default_import} from '{module_name}';",
                        'component_name': default_import,
                        'alias': None
                    })
                    
                    # 添加命名导入
                    for named_import in named_imports:
                        named_import = named_import.strip()
                        if named_import:
                            optimized_imports.append({
                                'import_type': 'named',
                                'module_name': module_name,
                                'full_import': f"import {{ {named_import} }} from '{module_name}';",
                                'component_name': named_import,
                                'alias': None
                            })
                else:
                    optimized_imports.append(ref)
            
            analysis.imports = optimized_imports
            complete_functions = []
            ui_with_imports = []
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
                r'(?m)^\s*'  # 行首空白
                r'(?:(?:@\w+\s+)*'  # 多个装饰器
                r'(?:(?:private|public|readonly|export)\s+)?'  # 单个访问修饰符
                r'(?:static\s+)?'  # 单个static修饰符
                r'(?:const|let|val|var)\s+'  # 变量声明关键字（只能有一个）
                r'(\w+)\s*:\s*'  # 变量名和类型声明
                r'([^=;\n{]+)'  # 类型声明
                r'(?:\s*=\s*([^;\n{]+))?'  # 可选的初始化值
                r'\s*;?\s*$)'  # 行尾
            )
            
            for match in variable_pattern.finditer(file_contents):
                if match.group(1) in reserved_words:
                    continue
                    
                # 检查是否在类或接口定义内
                context = file_contents[max(0, match.start()-100):match.start()]
                if re.search(r'class\s+\w+\s*{|interface\s+\w+\s*{', context):
                    continue
                    
                # 提取所有修饰符
                modifiers = []
                full_match = match.group(0)
                if '@' in full_match:
                    modifiers.extend(re.findall(r'@\w+', full_match))
                if 'private' in full_match:
                    modifiers.append('private')
                elif 'public' in full_match:  # 使用elif确保不会同时添加
                    modifiers.append('public')
                if 'readonly' in full_match:
                    modifiers.append('readonly')
                if 'export' in full_match:
                    modifiers.append('export')
                if 'static' in full_match:
                    modifiers.append('static')
                
                variable = {
                    'modifiers': modifiers,
                    'name': match.group(1).strip(),
                    'type': match.group(2).strip(),
                    'value': match.group(3).strip() if match.group(3) else None
                }
                analysis.add_variable(variable)

            # Extract function declarations and complete them with imports and variables
            function_pattern = re.compile(
                r'(\w+\s)?(\w+\s?)(=\s?)?\(\s?((\.\.\.)?((\w+\??\s?:\s?[^)]+\s?)(,\s?\w+\??\s?:\s?[^)]+)*)?)\)\s*?\s?(=>\s?)?(:\s?\w+\s?)?\{')
            for match in function_pattern.finditer(file_contents):
                function_name = match.group(2).strip() if match.group(2) else None
                if function_name in reserved_words:
                    continue
                if function_name != 'build':
                    start_pos = match.end() - 1
                    end_pos = find_balanced_braces(file_contents, start_pos)
                    if match.group(1) and match.group(1).strip() == 'Builder':
                        continue
                    if end_pos != -1:
                        if function_name and file_contents[start_pos:end_pos + 1].strip():
                            function = file_contents[match.start():end_pos + 1].strip()
                            
                            # 补全函数
                            function_content = function
                            used_imports = set()
                            used_variables = set()
                            
                            # 检查函数中使用的导入
                            for imp in analysis.imports:
                                if imp['component_name'] in function_content:
                                    used_imports.add(imp['full_import'])
                            
                            # 检查函数中使用的变量
                            for var in analysis.variables:
                                if var['name'] in function_content:
                                    # 构建变量声明
                                    var_declaration = []
                                    if var['modifiers']:
                                        var_declaration.extend(var['modifiers'])
                                    var_declaration.append(f"{var['name']}: {var['type']}")
                                    if var['value']:
                                        var_declaration.append(f"= {var['value']}")
                                    used_variables.add(' '.join(var_declaration))
                            
                            # 组合补全后的函数
                            if used_imports or used_variables:
                                complete_function = []
                                if used_imports:
                                    complete_function.extend(used_imports)
                                if used_variables:
                                    complete_function.extend(used_variables)
                                complete_function.append(function)
                                function = '\n'.join(complete_function)
                            
                            analysis.add_function(function)

            return analysis
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")




