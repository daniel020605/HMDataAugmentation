import os
import re
import json
import uuid

from ArkTSAbstractor.importAnalyzer import analyze_imports
from ArkTSAbstractor.logger import setup_logger, log_directory
from tool import load_reserved_words
from dependencyResolver import DependencyResolver
# 结果输出路径
function_folder = './complete_function'
ui_folder = './ui_with_import'
# 保留字加载
reserved_words = load_reserved_words()
# 日志
logger = setup_logger('file_analyzer_logger', os.path.join(log_directory, 'file_analyzer.log'))

class ETSFileAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_content = None
        self.file_type = None
        self.ui_code = []  # 现在存储的是包含完整信息的字典
        self.variables = []
        self.functions = []  # 现在存储的是包含完整信息的字典
        self.imports = []
        self.classes = []
        self.structs = []
        self.modules = []

    def set_file_content(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.file_content = file.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            self.file_content = None

    def set_file_type(self, file_type):
        self.file_type = file_type

    def add_ui_code(self, ui_code, dependencies=None):
        ui_info = {
            'id': str(uuid.uuid4()),
            'content': ui_code,
            'dependencies': dependencies or {
                'imports': [],
                'variables': [],
                'functions': [],
                'classes': [],
                'interfaces': []
            }
        }
        self.ui_code.append(ui_info)

    def add_variable(self, variable, dependencies=None):
        variable['dependencies'] = dependencies or {
            'imports': [],
            'variables': [],
            'functions': [],
            'classes': [],
            'interfaces': []
        }
        self.variables.append(variable)

    def add_function(self, function, name=None, dependencies=None):
        function_info = {
            'id': str(uuid.uuid4()),
            'name': name,
            'content': function,
            'dependencies': dependencies or {
                'imports': [],
                'variables': [],
                'functions': [],
                'classes': [],
                'interfaces': []
            }
        }
        self.functions.append(function_info)

    def add_class_or_interface(self, declaration, dependencies=None):
        declaration['dependencies'] = dependencies or {
            'imports': [],
            'variables': [],
            'functions': [],
            'classes': [],
            'interfaces': []
        }
        self.classes.append(declaration)

    def add_class(self, class_info):
        self.classes.append(class_info)

    def add_struct(self, struct_info):
        self.structs.append(struct_info)

    def add_module(self, module_info):
        self.modules.append(module_info)


    def add_reference(self, import_type, module_name, full_import, component_name=None, alias=None):
        reference = {
            'import_type': import_type,
            'module_name': module_name,
            'full_import': full_import,
            'name': component_name,
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
            # todo:函数识别逻辑需要优化
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

def process_resource_references(content, resource_dir):
    """处理资源引用
    Args:
        content: 文件内容
        resource_dir: 资源目录路径
    Returns:
        处理后的内容
    """
    try:
        # 处理media资源引用
        # media_pattern = r'\$r\([\'"](app\.media\.[^\'"]+)[\'"]\)'
        # content = re.sub(media_pattern, r'$r("app.media.startIcon")', content)

        # 处理element资源引用
        element_pattern = r'\$r\([\'"](app\.[^\'"]+)[\'"]\)'
        
        def replace_element_value(match):
            try:
                resource_path = match.group(1)
                # 从路径中提取键名和name
                _, key_name, name = resource_path.split('.')
                if key_name == 'media':
                    return f'$r("app.media.startIcon")'
                # 构建json文件路径
                json_path = os.path.join(resource_dir, 'element', f'{key_name}.json')
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 查找匹配的键名和name
                        for item in data.get(key_name, []):
                            if item.get('name') == name:
                                return f'"{item.get("value")}"'
                # print(json_path)
                return match.group(0)  # 如果找不到对应的value，保持原样

            except Exception as e:
                logger.error(f"Error processing element resource: {str(e)}")
                return match.group(0)

        content = re.sub(element_pattern, replace_element_value, content)
        return content
    except Exception as e:
        logger.error(f"Error processing resource references: {str(e)}")
        return content

def analyze_dependencies(content, analysis):
    """分析代码块中的依赖关系"""
    dependencies = {
        'imports': [],
        'variables': [],
        'functions': [],
        'classes': [],
        'interfaces': []
    }

    # 检查导入依赖
    for imp in analysis.imports:
        if imp.get('name') and imp['name'] in content:
            dependencies['imports'].append(imp)

    # 检查变量依赖
    for var in analysis.variables:
        if var.get('name') and var['name'] in content:
            dependencies['variables'].append(var)

    # 检查函数依赖
    for func in analysis.functions:
        if func.get('name') and func['name'] in content:
            dependencies['functions'].append(func)

    # 检查类依赖
    for cls in analysis.classes:
        if cls.get('name') and cls['name'] in content:
            if cls.get('type') == 'interface':
                dependencies['interfaces'].append(cls)
            else:
                dependencies['classes'].append(cls)

    return dependencies

def remove_comments(content):
    """移除代码中的注释"""
    try:
        # 移除多行注释 /* ... */
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        
        # 移除单行注释 // ...
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # 移除空行
        content = re.sub(r'^\s*$\n', '', content, flags=re.MULTILINE)
        
        return content
    except Exception as e:
        logger.error(f"Error removing comments: {str(e)}")
        return content

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
        # 移除注释
        file_contents = remove_comments(file_contents)
        analysis = ETSFileAnalysis(file_path)
        references = analyze_imports(file_contents, file_path)

        # 获取资源目录路径
        file_dir = os.path.dirname(file_path)
        if 'entry/src/main' in file_dir:
            # 找到entry/src/main的位置
            main_pos = file_dir.find('entry/src/main')
            # 截取到entry/src/main/resources/base
            resource_dir = file_dir[:main_pos] + 'entry/src/main/resources/base'
        else:
            resource_dir = os.path.join(file_dir, '..', '..', 'resources', 'base')

        # 处理资源引用
        file_contents = process_resource_references(file_contents, resource_dir)

        # 优化导入语句
        analysis.imports = references.references
        # 提取类、结构体和导出模块
        # 1. 提取类定义
        class_pattern = re.compile(r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{')
        for match in class_pattern.finditer(file_contents):
            try:
                class_name = match.group(1)
                parent_class = match.group(2)
                interfaces = [i.strip() for i in match.group(3).split(',')] if match.group(3) else []

                # 找到类的结束位置
                start_pos = match.end() - 1
                end_pos = find_balanced_braces(file_contents, start_pos)
                if end_pos != -1:
                    class_content = file_contents[match.start():end_pos + 1].strip()
                    class_info = {
                        'name': class_name,
                        'parent_class': parent_class,
                        'interfaces': interfaces,
                        'content': class_content
                    }
                    analysis.add_class(class_info)
            except Exception as e:
                logger.error(f"Error processing class in {file_path}: {str(e)}")
                continue

        # 2. 提取结构体定义
        struct_pattern = re.compile(r'@Component\s*(export)?\s*struct\s+(\w+)(?:\s+implements\s+([^{]+))?\s*\{')
        for match in struct_pattern.finditer(file_contents):
            try:
                struct_name = match.group(2)
                interfaces = [i.strip() for i in match.group(3).split(',')] if match.group(3) else []
                is_export = bool(match.group(1))

                # 找到结构体的结束位置
                start_pos = match.end() - 1
                end_pos = find_balanced_braces(file_contents, start_pos)
                if end_pos != -1:
                    struct_content = file_contents[match.start():end_pos + 1].strip()
                    struct_info = {
                        'name': struct_name,
                        'interfaces': interfaces,
                        'is_export': is_export,
                        'content': struct_content
                    }
                    analysis.add_struct(struct_info)
            except Exception as e:
                logger.error(f"Error processing struct in {file_path}: {str(e)}")
                continue

        # 3. 提取导出模块
        module_pattern = re.compile(r'export\s+module\s+(\w+)\s*\{')
        for match in module_pattern.finditer(file_contents):
            try:
                module_name = match.group(1)

                # 找到模块的结束位置
                start_pos = match.end() - 1
                end_pos = find_balanced_braces(file_contents, start_pos)
                if end_pos != -1:
                    module_content = file_contents[match.start():end_pos + 1].strip()
                    module_info = {
                        'name': module_name,
                        'content': module_content
                    }
                    analysis.add_module(module_info)
            except Exception as e:
                logger.error(f"Error processing module in {file_path}: {str(e)}")
                continue

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
                try:
                    match_start = match.start()
                    start_pos = match.end() - 1
                    end_pos = find_balanced_braces(file_contents, start_pos)
                    if end_pos != -1:
                        # 提取UI代码
                        ui_code = file_contents[match_start:end_pos + 1].strip()
                        if not ui_code:  # 如果UI代码为空，跳过
                            continue
                        # dependencies = analyze_dependencies(ui_code, analysis)
                        dependencies = None
                        analysis.add_ui_code(ui_code, dependencies)

                        # # 检查UI代码中使用的导入和变量
                        # used_imports = []
                        # used_variables = []
                        #
                        # # 检查UI代码中使用的导入
                        # for imp in analysis.imports:
                        #     if imp.get('name') and imp['name'] in ui_code:
                        #         used_imports.append(imp)
                        #
                        # # 检查UI代码中使用的变量
                        # for var in analysis.variables:
                        #     if var.get('name') and var['name'] in ui_code:
                        #         used_variables.append(var)
                        #
                        # # 保存UI代码及其依赖信息
                        # analysis.add_ui_code(ui_code, used_imports, used_variables)
                        # 记录需要删除的区间
                        matches.append((match_start, end_pos + 1))
                except Exception as e:
                    logger.error(f"Error processing UI code in {file_path}: {str(e)}")
                    continue

        # 按起始位置逆序排序，确保从后往前处理
        matches.sort(reverse=True, key=lambda x: x[0])

        # 从文件内容中删除所有记录的UI代码块
        for start, end in matches:
            file_contents = file_contents[:start] + file_contents[end:]


        # 识别接口声明
        interface_pattern = re.compile(
            r'(?:export\s+)?interface\s+(\w+)'  # 接口名
            r'(?:\s+extends\s+([^{]+))?'  # 可选的继承
            r'\s*\{'  # 开始大括号
        )

        for match in interface_pattern.finditer(file_contents):
            try:
                interface_name = match.group(1)
                extends = [x.strip() for x in match.group(2).split(',')] if match.group(2) else []

                # 找到接口主体
                start_pos = match.end() - 1
                end_pos = find_balanced_braces(file_contents, start_pos)

                if end_pos != -1:
                    interface_content = file_contents[match.start():end_pos + 1].strip()
                    interface_info = {
                        'type': 'interface',
                        'name': interface_name,
                        'extends': extends,
                        'content': interface_content,
                        'is_export': 'export' in match.group(0)
                    }
                    analysis.add_class_or_interface(interface_info)
            except Exception as e:
                logger.error(f"Error processing interface in {file_path}: {str(e)}")
                continue

        # 识别类声明
        class_pattern = re.compile(
            r'(?:export\s+)?class\s+(\w+)'  # 类名
            r'(?:\s+extends\s+(\w+))?'  # 可选的继承
            r'(?:\s+implements\s+([^{]+))?'  # 可选的接口实现
            r'\s*\{'  # 开始大括号
        )

        for match in class_pattern.finditer(file_contents):
            try:
                class_name = match.group(1)
                extends = match.group(2) if match.group(2) else None
                implements = [x.strip() for x in match.group(3).split(',')] if match.group(3) else []

                # 找到类主体
                start_pos = match.end() - 1
                end_pos = find_balanced_braces(file_contents, start_pos)

                if end_pos != -1:
                    class_content = file_contents[match.start():end_pos + 1].strip()
                    # dependencies = analyze_dependencies(class_content, analysis)
                    dependencies = None
                    class_info = {
                        'type': 'class',
                        'name': class_name,
                        'extends': extends,
                        'implements': implements,
                        'content': class_content,
                        'is_export': 'export' in match.group(0)
                    }
                    analysis.add_class_or_interface(class_info, dependencies)
            except Exception as e:
                logger.error(f"Error processing class in {file_path}: {str(e)}")
                continue

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

                # 获取变量声明的位置
                var_start = match.start()

                # 检查是否在接口或类定义内
                is_in_interface = False
                for interface_info in analysis.classes:
                    if interface_info.get('type') == 'interface':
                        interface_content = interface_info.get('content', '')
                        # 找到接口内容在原文件中的位置
                        interface_pos = file_contents.find(interface_content)
                        if interface_pos != -1 and interface_pos < var_start < interface_pos + len(interface_content):
                            is_in_interface = True
                            break

                if is_in_interface:
                    continue  # 如果在接口定义内，跳过这个变量声明

                # 检查是否在函数调用参数中
                context = file_contents[max(0, match.start() - 100):match.start()]
                if re.search(r'\w+\s*\([^)]*$', context):  # 检查是否在函数调用的括号内
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

                variable_name = match.group(1).strip()
                variable_type = match.group(2).strip() if match.group(2) else None
                variable_value = match.group(3).strip() if match.group(3) else None

                # 检查变量值是否为列表
                if variable_value and variable_value == '[':
                    start_pos = match.end() - 1
                    brace_count = 0
                    for i in range(start_pos, len(file_contents)):
                        if file_contents[i] == '[':
                            brace_count += 1
                        elif file_contents[i] == ']':
                            brace_count -= 1
                        if brace_count == 0:
                            variable_value = file_contents[start_pos:i + 1].strip()
                            break

                variable = {
                    'modifiers': modifiers,
                    'name': variable_name,
                    'type': variable_type,
                    'value': variable_value,
                    'full_variable': match.group(0)
                }
                # dependencies = analyze_dependencies(match.group(0), analysis)
                dependencies = None
                analysis.add_variable(variable, dependencies)

            except Exception as e:
                logger.error(f"Error processing variable in {file_path}: {str(e)}")
                continue

        # 保留函数，用于解决Circular Dependencies的问题
        reserved_functions = {
            'build',
            'Column',
            'Row',
            'Text',
            'Image',
            'TextInput',
            'Button',
        }
        # Extract function declarations
        function_pattern = re.compile(
            r'(\w+\s)?(\w+\s?)(=\s?)?\(\s?((\.\.\.)?((\w+\??\s?:\s?[^)]+\s?)(,\s?\w+\??\s?:\s?[^)]+)*)?)\)\s*?\s?(=>\s?)?(:\s?\w+\s?)?\{')
        for match in function_pattern.finditer(file_contents):
            try:
                function_name = match.group(2).strip() if match.group(2) else None
                if (not function_name or
                        function_name in reserved_words or
                        function_name in reserved_functions):  # Add reserved functions check
                    continue

                if function_name != 'build':
                    start_pos = match.end() - 1
                    end_pos = find_balanced_braces(file_contents, start_pos)
                    if match.group(1) and match.group(1).strip() == 'Builder':
                        continue
                    if end_pos != -1:
                        if function_name and file_contents[start_pos:end_pos + 1].strip():
                            function = file_contents[match.start():end_pos + 1].strip()
                            analysis.add_function(function, function_name)

                            #
                            # # 检查函数中使用的导入和变量
                            # used_imports = []
                            # used_variables = []
                            #
                            # # 检查函数中使用的导入
                            # for imp in analysis.imports:
                            #     if imp.get('name') and imp['name'] in function:
                            #         used_imports.append(imp)
                            #
                            # # 检查函数中使用的变量
                            # for var in analysis.variables:
                            #     if var.get('name') and var['name'] in function:
                            #         used_variables.append(var)
                            #
                            # # 保存函数及其依赖信息
                            # analysis.add_function(function, used_imports, used_variables, function_name)
            except Exception as e:
                logger.error(f"Error processing function in {file_path}: {str(e)}")
                continue

        def get_immediate_dependencies(item):
            """Returns list of items that this item directly depends on based on type"""
            content = item.get('content', '')
            item_type = item.get('type', '')
            file_name = os.path.basename(file_path)
            base_name = os.path.splitext(file_name)[0] if file_name else ''  # Remove extension
            deps = []

            # Imports have no dependencies
            if 'import_type' in item:
                return []

            # Classes and Interfaces can only depend on imports
            elif item_type in ['class', 'interface']:
                for imp in analysis.imports:
                    if imp.get('name') and imp['name'] in content:
                        # Skip if import name matches file name
                        if imp['name'] != base_name:
                            deps.append(imp)

            # Variables can depend on imports, functions, classes, and interfaces
            elif 'full_variable' in item:
                # Check import dependencies
                for imp in analysis.imports:
                    if imp.get('name') and imp['name'] in content:
                        if imp['name'] != base_name:
                            deps.append(imp)

                # Check function dependencies
                for func in analysis.functions:
                    if func.get('name') and func['name'] in content:
                        if func['name'] != base_name:
                            deps.append(func)

                # Check class/interface dependencies
                for cls in analysis.classes:
                    if cls['name'] in content:
                        if cls['name'] != base_name:
                            deps.append(cls)

            # Functions can depend on imports, other functions, classes, and interfaces
            elif 'name' in item and 'content' in item:  # Function case
                # Check import dependencies
                for imp in analysis.imports:
                    if imp.get('name') and imp['name'] in content:
                        if imp['name'] != base_name:
                            deps.append(imp)

                # Check function dependencies (excluding self-reference)
                for func in analysis.functions:
                    if func.get('name') and func['name'] in content and func['name'] != item['name']:
                        if func['name'] != base_name:
                            deps.append(func)

                # Check class/interface dependencies
                for cls in analysis.classes:
                    if cls['name'] in content:
                        if cls['name'] != base_name:
                            deps.append(cls)

            return deps

        def analyze_item_dependencies(item):
            """Sets dependencies based on item type"""
            content = item.get('content', '')
            item_type = item.get('type', '')
            file_name = os.path.basename(file_path)

            base_name = os.path.splitext(file_name)[0] if file_name else ''
            dependencies = {
                'imports': [],
                'variables': [],
                'functions': [],
                'classes': [],
                'interfaces': []
            }

            # Imports have no dependencies
            if 'import_type' in item:
                return

            # Classes and Interfaces can only depend on imports
            elif item_type in ['class', 'interface']:
                for imp in analysis.imports:
                    if imp.get('name') and imp['name'] in content:
                        if imp['name'] != base_name:
                            dependencies['imports'].append(imp)

            # Variables and Functions can depend on imports, functions, classes, and interfaces
            else:
                for imp in analysis.imports:
                    if imp.get('name') and imp['name'] in content:
                        if imp['name'] != base_name:
                            dependencies['imports'].append(imp)

                # Only add function and class dependencies for variables and functions
                if 'full_variable' in item or ('name' in item and 'content' in item):
                    for func in analysis.functions:
                        if func.get('name') and func['name'] in content:
                            if ('name' not in item or func['name'] != item['name']) and func['name'] != base_name:
                                dependencies['functions'].append(func)

                    for cls in analysis.classes:
                        if cls['name'] in content:
                            if cls['name'] != base_name:
                                if cls.get('type') == 'interface':
                                    dependencies['interfaces'].append(cls)
                                else:
                                    dependencies['classes'].append(cls)

            item['dependencies'] = dependencies

        # === Third Pass: Resolve dependencies ===
        resolver = DependencyResolver()

        # Resolve class dependencies
        for cls in analysis.classes:
            resolver.resolve(cls, get_immediate_dependencies, analyze_item_dependencies, 1)

        # Resolve variable dependencies
        for var in analysis.variables:
            resolver.resolve(var, get_immediate_dependencies, analyze_item_dependencies, 1)

        # Resolve function dependencies
        for func in analysis.functions:
            resolver.resolve(func, get_immediate_dependencies, analyze_item_dependencies, 1)

        # Resolve UI code dependencies
        for ui in analysis.ui_code:
            resolver.resolve(ui, get_immediate_dependencies, analyze_item_dependencies, 1)

        return analysis
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        return None



if __name__ == '__main__':
    print(analyze_ets_file("/Users/liuxuejin/Downloads/gitee_cloned_repos_5min_stars/帝心_HarmonyOS应用开发教程/NEXT/base/NextBase/entry/src/main/ets/pages/ArkUI/TextDemo.ets").imports)