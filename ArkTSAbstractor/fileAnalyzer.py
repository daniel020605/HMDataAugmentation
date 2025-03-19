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

def resolve_relative_path(base_path, relative_path):
    """解析相对路径，返回绝对路径"""
    try:
        # 获取基础路径的目录
        base_dir = os.path.dirname(base_path)
        # 将相对路径转换为绝对路径
        absolute_path = os.path.abspath(os.path.join(base_dir, relative_path))
        return absolute_path + '.ets'
    except Exception as e:
        logger.error(f"Error resolving relative path: {str(e)}")
        return None

def find_component_or_function(file_path, component_name):
    """在文件中查找组件或函数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # 查找组件
            component_pattern = re.compile(r'@Component\s*(export)?\s*struct\s+' + re.escape(component_name))
            if component_pattern.search(content):
                # 找到组件，提取整个组件定义
                start_pos = content.find(f"struct {component_name}")
                end_pos = find_balanced_braces(content, start_pos + len(f"struct {component_name}"))
                if end_pos != -1:
                    return content[start_pos:end_pos + 1].strip()
            
            # 查找函数
            function_pattern = re.compile(r'function\s+' + re.escape(component_name) + r'\s*\(')
            if function_pattern.search(content):
                # 找到函数，提取整个函数定义
                start_pos = content.find(f"function {component_name}")
                end_pos = find_balanced_braces(content, start_pos + len(f"function {component_name}"))
                if end_pos != -1:
                    return content[start_pos:end_pos + 1].strip()
            
            return None
    except Exception as e:
        logger.error(f"Error finding component/function in {file_path}: {str(e)}")
        return None

def process_resource_references(content):
    """处理资源引用，将$r()替换为字符串常量"""
    try:
        # 匹配$r()模式的正则表达式
        resource_pattern = re.compile(r'\$r\([\'"]([^\'"]+)[\'"]\)')
        
        # 用于存储已处理的资源引用
        processed_resources = {}
        
        def replace_resource(match):
            resource_path = match.group(1)
            # 生成资源引用的常量名
            constant_name = f"RESOURCE_{resource_path.replace('.', '_').replace('/', '_').upper()}"
            # 存储资源引用信息
            processed_resources[constant_name] = resource_path
            # 返回替换后的字符串
            return f'"{constant_name}"'
        
        # 替换所有资源引用
        processed_content = resource_pattern.sub(replace_resource, content)
        
        return processed_content, processed_resources
    except Exception as e:
        logger.error(f"Error processing resource references: {str(e)}")
        return content, {}

def analyze_ets_file(file_path):
    # 尝试不同的编码方式
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'latin1']
    file_contents = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                file_contents = file.read()
                break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Error reading {file_path} with {encoding} encoding: {str(e)}")
            continue
    
    if file_contents is None:
        logger.error(f"Failed to read {file_path} with any supported encoding")
        return None
        
    try:
        file_basename = os.path.basename(file_path)
        analysis = ETSFileAnalysis(file_contents)
        references = analyze_imports(file_contents)
        
        # 优化导入语句
        optimized_imports = []
        for ref in references.references:
            try:
                if not ref.get('component_name'):  # 如果component_name为None或不存在
                    optimized_imports.append(ref)
                    continue
                    
                if ref['import_type'] == 'named':
                    module_name = ref['module_name']
                    # 检查是否为相对路径导入
                    if not module_name.startswith('@'):
                        # 解析相对路径
                        resolved_path = resolve_relative_path(file_path, module_name)
                        if resolved_path:
                            # 查找对应的组件或函数
                            component_content = find_component_or_function(resolved_path, ref['component_name'])
                            if component_content:
                                # 将找到的内容添加到导入中
                                ref['component_content'] = component_content
                    
                    # 检查是否包含多个组件
                    if ',' in ref['component_name']:
                        # 处理多个命名导入的情况
                        components = [c.strip() for c in ref['component_name'].split(',')]
                        for component in components:
                            if component:  # 确保组件名不为空
                                optimized_imports.append({
                                    'import_type': 'named',
                                    'module_name': module_name,
                                    'full_import': f"import {{ {component} }} from '{module_name}';",
                                    'component_name': component,
                                    'alias': None,
                                    'component_content': ref.get('component_content')
                                })
                    else:
                        # 单个命名导入
                        optimized_imports.append({
                            'import_type': 'named',
                            'module_name': module_name,
                            'full_import': f"import {{ {ref['component_name']} }} from '{module_name}';",
                            'component_name': ref['component_name'],
                            'alias': None,
                            'component_content': ref.get('component_content')
                        })
                elif ref['import_type'] == 'default' and '{' in ref['component_name']:
                    # 处理默认导入和命名导入混合的情况
                    module_name = ref['module_name']
                    # 分离默认导入和命名导入
                    parts = ref['component_name'].split(',')
                    if not parts:  # 如果parts为空，跳过这个导入
                        continue
                        
                    default_import = parts[0].strip()
                    if not default_import:  # 如果默认导入为空，跳过这个导入
                        continue
                        
                    # 添加默认导入
                    optimized_imports.append({
                        'import_type': 'default',
                        'module_name': module_name,
                        'full_import': f"import {default_import} from '{module_name}';",
                        'component_name': default_import,
                        'alias': None
                    })
                    
                    # 处理命名导入
                    if len(parts) > 1:  # 确保有命名导入部分
                        named_imports = parts[1].strip('{} ').split(',')
                        for named_import in named_imports:
                            named_import = named_import.strip()
                            if named_import:  # 确保命名导入不为空
                                optimized_imports.append({
                                    'import_type': 'named',
                                    'module_name': module_name,
                                    'full_import': f"import {{ {named_import} }} from '{module_name}';",
                                    'component_name': named_import,
                                    'alias': None
                                })
                else:
                    optimized_imports.append(ref)
            except Exception as e:
                logger.error(f"Error processing import in {file_path}: {str(e)}")
                continue

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
            # Extract variable declarations


        # Extract UI code blocks
        ui_code_patterns = [r'build\s*\(\)\s*\{', r'@Builder\s*\w+\s?\((\w+\s?:+\s?\w+)?\)\s*\{']
        matches = []

        # 收集所有匹配项及其对应的起始和结束位置
        for pattern in ui_code_patterns:
            for match in re.finditer(pattern, file_contents):
                try:
                    match_start = match.start()
                    start_pos = match.end() - 1
                    end_pos = find_balanced_braces(file_contents, start_pos)
                    if end_pos != -1:
                        # 提取UI代码
                        ui_code = file_contents[match_start:end_pos + 1].strip()
                        if not ui_code:  # 如果UI代码为空，跳过
                            continue
                            
                        # 补全UI代码
                        used_imports = set()
                        used_variables = set()
                        
                        # 检查UI代码中使用的导入
                        for imp in analysis.imports:
                            if imp.get('component_name') and imp['component_name'] in ui_code:
                                used_imports.add(imp['full_import'])
                        
                        # 检查UI代码中使用的变量
                        for var in analysis.variables:
                            if var.get('name') and var['name'] in ui_code:
                                # 构建变量声明
                                var_declaration = []
                                if var.get('modifiers'):
                                    var_declaration.extend(var['modifiers'])
                                if var.get('type'):
                                    var_declaration.append(f"{var['name']}: {var['type']}")
                                else:
                                    var_declaration.append(var['name'])
                                if var.get('value'):
                                    var_declaration.append(f"= {var['value']}")
                                used_variables.add(' '.join(var_declaration))
                        
                        # 组合补全后的UI代码
                        if used_imports or used_variables:
                            complete_ui = []
                            if used_imports:
                                complete_ui.extend(used_imports)
                            if used_variables:
                                complete_ui.extend(used_variables)
                            complete_ui.append(ui_code)
                            ui_code = '\n'.join(complete_ui)
                        
                        # 保存UI代码到分析对象
                        analysis.add_ui_code(ui_code)
                        # 记录需要删除的区间（起始和结束位置）
                        matches.append((match_start, end_pos + 1))
                except Exception as e:
                    logger.error(f"Error processing UI code in {file_path}: {str(e)}")
                    continue

        # 按起始位置逆序排序，确保从后往前处理
        matches.sort(reverse=True, key=lambda x: x[0])

        # 从文件内容中删除所有记录的UI代码块
        for start, end in matches:
            file_contents = file_contents[:start] + file_contents[end:]

        variable_pattern = re.compile(
            r'(?m)^\s*'  # 行首空白
            r'(?:(?:@\w+\s+)*'  # 多个装饰器
            r'(?:(?:private|public|readonly|export)\s+)?'  # 单个访问修饰符
            r'(?:static\s+)?'  # 单个static修饰符
            r'(?:(?:const|let|val|var)\s+)?'  # 可选的变量声明关键字
            r'(\w+)\s*\??:\s*'  # 变量名和类型声明
            r'([a-zA-Z_][^=;\n{]+)'  # 类型声明
            r'(?:\s*=\s*([^;\n{]+))?'  # 可选的初始化值
            r'\s*;?\s*$)'  # 行尾
        )

        for match in variable_pattern.finditer(file_contents):
            try:
                if not match.group(1):  # 如果变量名为空，跳过
                    continue

                if match.group(1) in reserved_words:
                    continue

                # 检查是否在类或接口定义内
                context = file_contents[max(0, match.start() - 100):match.start()]
                if re.search(r'class\s+\w+\s*{|interface\s+\w+\s*{', context):
                    continue

                # 提取所有修饰符
                modifiers = []
                full_match = match.group(0)
                # 提取装饰器
                if '@' in full_match:
                    modifiers.extend(re.findall(r'@\w+', full_match))
                # 提取访问修饰符
                if 'private' in full_match:
                    modifiers.append('private')
                elif 'public' in full_match:
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
                    'type': match.group(2).strip() if match.group(2) else None,
                    'value': match.group(3).strip() if match.group(3) else None,
                    'full_variable': match.group(0)
                }
                analysis.add_variable(variable)
            except Exception as e:
                logger.error(f"Error processing variable in {file_path}: {str(e)}")
                continue

        # Extract function declarations and complete them with imports and variables
        function_pattern = re.compile(
            r'(\w+\s)?(\w+\s?)(=\s?)?\(\s?((\.\.\.)?((\w+\??\s?:\s?[^)]+\s?)(,\s?\w+\??\s?:\s?[^)]+)*)?)\)\s*?\s?(=>\s?)?(:\s?\w+\s?)?\{')
        for match in function_pattern.finditer(file_contents):
            try:
                function_name = match.group(2).strip() if match.group(2) else None
                if not function_name or function_name in reserved_words:
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
                            if not function_content:  # 如果函数内容为空，跳过
                                continue
                                
                            used_imports = set()
                            used_variables = set()
                            
                            # 检查函数中使用的导入
                            for imp in analysis.imports:
                                if imp.get('component_name') and imp['component_name'] in function_content:
                                    used_imports.add(imp['full_import'])
                            
                            # 检查函数中使用的变量
                            for var in analysis.variables:
                                if var.get('name') and var['name'] in function_content:
                                    # 构建变量声明
                                    # var_declaration = []
                                    # if var.get('modifiers'):
                                    #     var_declaration.extend(var['modifiers'])
                                    # if var.get('type'):
                                    #     var_declaration.append(f"{var['name']}: {var['type']}")
                                    # else:
                                    #     var_declaration.append(var['name'])
                                    # if var.get('value'):
                                    #     var_declaration.append(f"= {var['value']}")
                                    # used_variables.add(' '.join(var_declaration))
                                    used_variables.add(var['full_variable'])

                            # 组合补全后的函数
                            # if used_imports or used_variables:
                            #     complete_function = []
                            #     if used_imports:
                            #         complete_function.extend(used_imports)
                            #     if used_variables:
                            #         complete_function.extend(used_variables)
                            #     complete_function.append(function)
                            #     function = '\n'.join(complete_function)
                            
                            analysis.add_function(function)
            except Exception as e:
                logger.error(f"Error processing function in {file_path}: {str(e)}")
                continue

        # 处理UI代码和函数的补全
        def complete_code_with_imports(code_content):
            if not code_content:
                return code_content
                
            used_imports = set()
            used_variables = set()
            used_components = set()
            
            # 处理资源引用
            processed_content, resource_constants = process_resource_references(code_content)
            
            # 检查代码中使用的导入
            for imp in analysis.imports:
                if imp.get('component_name') and imp['component_name'] in processed_content:
                    used_imports.add(imp['full_import'])
                    # 如果有组件内容，添加到used_components
                    if imp.get('component_content'):
                        used_components.add(imp['component_content'])
            
            # 检查代码中使用的变量
            for var in analysis.variables:
                if var.get('name') and var['name'] in processed_content:
                    # 构建变量声明
                    # var_declaration = []
                    # if var.get('modifiers'):
                    #     var_declaration.extend(var['modifiers'])
                    # if var.get('type'):
                    #     var_declaration.append(f"{var['name']}: {var['type']}")
                    # else:
                    #     var_declaration.append(var['name'])
                    # if var.get('value'):
                    #     var_declaration.append(f"= {var['value']}")
                    # used_variables.add(' '.join(var_declaration))
                    used_variables.add(var['full_variable'])
            
            # 组合补全后的代码
            if used_imports or used_variables or used_components or resource_constants:
                complete_code = []
                if used_imports:
                    complete_code.extend(used_imports)
                if used_variables:
                    complete_code.extend(used_variables)
                if used_components:
                    complete_code.extend(used_components)
                if resource_constants:
                    # 添加资源常量声明
                    resource_declarations = []
                    for constant_name, resource_path in resource_constants.items():
                        resource_declarations.append(f"const {constant_name} = '{resource_path}';")
                    complete_code.extend(resource_declarations)
                complete_code.append(processed_content)
                return '\n'.join(complete_code)
            
            return processed_content

        # 补全UI代码
        # for i, ui_code in enumerate(analysis.ui_code):
        #     analysis.ui_code[i] = complete_code_with_imports(ui_code)

        # 补全函数
        # for i, function in enumerate(analysis.functions):
        #     analysis.functions[i] = complete_code_with_imports(function)

        return analysis
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        return None  # 返回None而不是抛出异常



if __name__ == '__main__':
    print(analyze_ets_file("/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/test/tt/Index.ets").variables)