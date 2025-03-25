import re
import os
from ArkTSAbstractor.logger import setup_logger, log_directory

logger = setup_logger('import_analyzer_logger', os.path.join(log_directory, 'import_analyzer.log'))

class ImportAnalysis:
    def __init__(self):
        self.references = []

    def add_reference(self, import_type, module_name, full_import, component_name=None, alias=None):
        reference = {
            'import_type': import_type,
            'module_name': module_name,
            'full_import': full_import,
            'component_name': component_name,
            'alias': alias
        }
        self.references.append(reference)

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

def optimize_imports(references, file_path):
    """优化导入语句
    Args:
        references: 原始导入引用列表
        file_path: 当前文件路径
    Returns:
        优化后的导入引用列表
    """
    optimized_imports = []
    for ref in references:
        component_name = ref['component_name']
        bracket_pattern = re.compile(rf'(\{{[\w\s,]*{re.escape(component_name)}[\w\s,]*\}})')
        if bracket_pattern.search(ref['full_import']):
            # 处理命名导入
            full_import = f"import {{ {ref['component_name']} }} from '{ref['module_name']}';"
            optimized_imports.append({
                'import_type': ref['import_type'],
                'module_name': ref['module_name'],
                'full_import': full_import,
                'component_name': ref['component_name'],
                'alias': ref['alias'],
                'component_content': None
            })
        else:
            # 处理默认导入
            full_import = f"import {ref['component_name']} from '{ref['module_name']}';"
            optimized_imports.append({
                'import_type': ref['import_type'],
                'module_name': ref['module_name'],
                'full_import': full_import,
                'component_name': ref['component_name'],
                'alias': ref['alias'],
                'component_content': None
            })
    return optimized_imports        

def analyze_imports(content, file_path):
    """分析文件中的导入语句
    Args:
        content: 文件内容
        file_path: 当前文件路径
    Returns:
        优化后的导入分析结果
    """
    analysis = ImportAnalysis()
    
    # 匹配导入语句的正则表达式
    import_pattern = re.compile(
        r'import\s*'  # import关键字，允许任意空白
        r'(?:(\w+)\s*,\s*)?'  # 可选的默认导入
        r'(?:\{([^}]+)\})?'  # 可选的命名导入
        r'\s+from\s+[\'"]([^\'"]+)[\'"]'  # 模块路径
    )

    # 查找所有导入语句
    for match in import_pattern.finditer(content):
        try:
            default_import = match.group(1)
            named_imports = match.group(2)
            module_name = match.group(3)

            # 处理默认导入
            if default_import:
                analysis.add_reference(
                    import_type='default',
                    module_name=module_name,
                    full_import=match.group(0),
                    component_name=default_import
                )

            # 处理命名导入
            if named_imports:
                # 处理多个命名导入
                components = [c.strip() for c in named_imports.split(',')]
                for component in components:
                    if component:
                        analysis.add_reference(
                            import_type='named',
                            module_name=module_name,
                            full_import=match.group(0),
                            component_name=component
                        )
        except Exception as e:
            logger.error(f"Error processing import match: {str(e)}")
            continue

    # 优化导入语句
    # 调用 optimize_imports 函数进行优化
    optimized_references = optimize_imports(analysis.references, file_path)
    # 更新分析结果中的引用列表
    analysis.references = optimized_references
    return analysis
