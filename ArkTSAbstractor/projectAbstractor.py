import os
import json
from tqdm import tqdm
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging
import uuid


from ArkTSAbstractor.fileAnalyzer import analyze_ets_file
from ArkTSAbstractor.tool import check_project_version

@dataclass
class ProjectStats:
    total_projects: int = 0
    processed_projects: int = 0
    failed_projects: int = 0
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0

class ProjectAbstractor:
    def __init__(self, output_dir: Path, log_dir: Path):
        self.output_dir = output_dir
        self.log_dir = log_dir
        self.stats = ProjectStats()
        self.setup_logging()

    def setup_logging(self):
        """设置日志记录"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置文件处理日志
        self.file_logger = logging.getLogger('file_logger')
        file_handler = logging.FileHandler(self.log_dir / 'file_errors.log')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.file_logger.addHandler(file_handler)
        self.file_logger.setLevel(logging.ERROR)
        
        # 设置版本检查日志
        self.version_logger = logging.getLogger('version_logger')
        version_handler = logging.FileHandler(self.log_dir / 'version_errors.log')
        version_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.version_logger.addHandler(version_handler)
        self.version_logger.setLevel(logging.ERROR)

    def get_ets_files(self, project_path: Path) -> List[Path]:
        """获取项目中的所有.ets文件"""
        return list(project_path.rglob('*.ets'))

    def analyze_ets_file(self, file_path: Path) -> Optional[Dict]:
        """分析单个.ets文件"""
        try:
            analysis = analyze_ets_file(str(file_path))
            if analysis:
                return {
                    'id': str(uuid.uuid4()),
                    'file': str(file_path),
                    'file_type': analysis.file_type,
                    'ui_code': analysis.ui_code,
                    'variables': analysis.variables,
                    'functions': analysis.functions,
                    'imports': analysis.imports,
                    'classes': analysis.classes,
                }
        except Exception as e:
            self.file_logger.error(f"分析文件 {file_path} 时出错: {e}")
            self.stats.failed_files += 1
        return None

    def analyze_project(self, project_path: Path) -> bool:
        """分析单个项目"""
        try:
            project_name = project_path.name
            output_file = self.output_dir / f'{project_name}.json'

            if not check_project_version(str(project_path)):
                return False

            ets_files = self.get_ets_files(project_path)
            self.stats.total_files += len(ets_files)

            project_analysis = []
            with ThreadPoolExecutor() as executor:
                for result in executor.map(self.analyze_ets_file, ets_files):
                    if result:
                        project_analysis.append(result)
                        self.stats.processed_files += 1

            # 在所有文件分析完成后解析内部依赖
            if project_analysis:
                try:
                    self.resolve_internal_imports(project_analysis)  # 添加依赖解析步骤

                    # # 在JSON序列化前移除所有循环引用
                    # cleaned_data = self.remove_circular_references(project_analysis)
                    #
                    # output_file.parent.mkdir(parents=True, exist_ok=True)
                    # with open(output_file, 'w', encoding='utf-8') as f:
                    #     json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

                    # 移除循环引用
                    self.file_logger.info("开始移除循环引用...")
                    clean_data = self.remove_circular_references(project_analysis)
                    self.file_logger.info("循环引用处理完成")

                    # 写入JSON文件
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(clean_data, f, indent=2, ensure_ascii=False)

                    with open(self.log_dir / 'processed_projects.log', 'a', encoding='utf-8') as f:
                        f.write(f"{project_name}\n")

                    self.stats.processed_projects += 1
                    return True
                except Exception as e:
                    self.file_logger.error(f"解析或序列化项目 {project_path} 时出错: {e}")
                    # self.file_logger.error(f"处理失败: {str(e)}")
                    import traceback
                    self.file_logger.error(traceback.format_exc())
                    self.stats.failed_projects += 1

        except Exception as e:
            self.file_logger.error(f"处理项目 {project_path} 时出错: {e}")
            self.stats.failed_projects += 1
        return False

    def resolve_internal_imports(self, project_analysis):
        """使用迭代而非递归解析内部依赖，避免栈溢出"""
        file_map = {item['file']: item for item in project_analysis}
        processed_refs = set()  # 跟踪已处理的引用
        MAX_DEPTH = 3  # 最大允许深度

        # 使用队列代替递归
        from collections import deque
        queue = deque()

        # 初始化队列 - 所有文件从深度0开始
        for file_path in file_map:
            queue.append((file_path, 0))  # (文件路径, 当前深度)

        # 处理队列
        while queue:
            file_path, depth = queue.popleft()

            # 深度限制检查
            if depth > MAX_DEPTH:
                self.file_logger.warning(f"跳过深度过大的引用: {file_path}, 深度={depth}")
                continue

            item = file_map.get(file_path)
            if not item:
                continue

            for imp in item.get('imports', []):
                module_name = imp.get('module_name', '')
                if not module_name.startswith('.'):  # 只处理内部依赖
                    continue

                # 解析绝对路径
                base_path = os.path.dirname(file_path)
                absolute_path = os.path.abspath(os.path.join(base_path, module_name)) + '.ets'
                if absolute_path not in file_map:
                    imp['resolved_file'] = None
                    continue

                imp['resolved_file'] = absolute_path
                name_to_find = imp.get('name')
                if not name_to_find:
                    continue

                # 生成引用唯一标识符
                ref_key = f"{absolute_path}:{name_to_find}"
                # 在循环引用检测处
                if ref_key in processed_refs:
                    # 跳过已处理的引用，但保留基本信息和代码内容
                    self.file_logger.info(f"跳过重复引用: {ref_key}")

                    # 获取包含代码内容的基本信息
                    component_info = self.extract_basic_info(file_map, absolute_path, name_to_find)
                    imp['component_content'] = {
                        "circular_ref": True,
                        "basic_info": component_info,
                        "ref_module": module_name,
                        "ref_name": name_to_find,
                        # 将代码内容从basic_info提升到顶层
                        "content": component_info.get("content", ""),
                    }
                    continue

                processed_refs.add(ref_key)

                # 查找匹配项
                resolved_item = file_map[absolute_path]
                for module in ['variables', 'functions', 'classes']:
                    for entry in resolved_item.get(module, []):
                        if entry.get('name') == name_to_find:
                            # 使用已存在的ID或创建新ID
                            ref_id = entry.get('id')
                            if not ref_id:
                                ref_id = str(uuid.uuid4())
                                entry['id'] = ref_id

                            # 创建完整引用
                            imp['component_content'] = {
                                'reference_id': ref_id,
                                'name': entry.get('name', ''),
                                'type': entry.get('type', ''),
                                'file': absolute_path,
                                'is_reference': True,
                                'content_type': module[:-1],  # 'variable', 'function', or 'class'
                                'properties': entry.get('properties', [])[:3] if 'properties' in entry else []
                            }

                            # 将被引用文件加入队列，增加深度
                            queue.append((absolute_path, depth + 1))
                            break

    def extract_basic_info(self, file_map, file_path, name):
        """提取组件的基本信息和代码内容，避免循环引用"""
        resolved_item = file_map.get(file_path)
        if not resolved_item:
            return {"name": name, "status": "file_not_found"}

        for module in ['variables', 'functions', 'classes']:
            for entry in resolved_item.get(module, []):
                if entry.get('name') == name:
                    basic_info = {
                        "name": name,
                        "type": entry.get('type', ''),
                        "content_type": module[:-1],  # 'variable', 'function', or 'class'
                    }

                    # 添加代码内容 - 这是关键修改
                    if "content" in entry:
                        basic_info["content"] = entry["content"]

                    # 添加特定类型的信息
                    if module == 'functions':
                        basic_info["params_count"] = len(entry.get('params', []))
                        basic_info["params"] = entry.get('params', [])
                    elif module == 'classes':
                        basic_info["methods_count"] = len(entry.get('methods', []))
                        basic_info["properties_count"] = len(entry.get('properties', []))
                        # 可以选择性添加一些方法和属性
                        if len(entry.get('methods', [])) > 0:
                            basic_info["methods_sample"] = [m.get('name') for m in entry.get('methods', [])[:3]]

                    return basic_info

        return {"name": name, "status": "not_found_in_file"}

    def remove_circular_references(self, data, max_depth=15):
        """彻底清除数据结构中的循环引用，同时保留基本信息"""
        visited = {}  # 使用共享字典跟踪已访问对象

        # 预先保存顶层imports信息的副本
        top_level_imports = {}
        for i, item in enumerate(data):
            if 'imports' in item and isinstance(item['imports'], list):
                top_level_imports[id(item['imports'])] = True
                for j, imp in enumerate(item['imports']):
                    if isinstance(imp, dict):
                        imp_id = id(imp)
                        top_level_imports[imp_id] = True

        def _remove_refs(obj, depth=0, path="root"):
            # 基本类型直接返回
            if obj is None or isinstance(obj, (str, int, float, bool)):
                return obj

            # 检查递归深度
            if depth > max_depth:
                self.file_logger.warning(f"达到最大递归深度 {max_depth} at {path}")
                return {"max_depth_reached": True}

            # 获取对象ID
            obj_id = id(obj)

            # 顶层imports的特殊处理
            is_top_import = obj_id in top_level_imports

            # 检测循环引用，但对顶层imports保留特殊处理
            if obj_id in visited:
                self.file_logger.warning(f"截断循环引用: {path} -> {visited[obj_id]}")

                # 如果是顶层imports对象，保留关键字段
                if is_top_import and isinstance(obj, dict):
                    preserved = {
                        "name": obj.get("name", ""),
                        "module_name": obj.get("module_name", ""),
                        "import_type": obj.get("import_type", ""),
                        "resolved_file": obj.get("resolved_file", ""),
                    }

                    # 保留组件内容的基本信息和代码
                    if "component_content" in obj and isinstance(obj["component_content"], dict):
                        # 获取代码内容
                        content = obj["component_content"].get("content", "")
                        if not content and "basic_info" in obj["component_content"]:
                            content = obj["component_content"]["basic_info"].get("content", "")

                        preserved["component_content"] = {
                            "circular_ref": True,
                            "name": obj["component_content"].get("name", ""),
                            "type": obj["component_content"].get("type", ""),
                            "content_type": obj["component_content"].get("content_type", ""),
                            "ref_path": visited[obj_id],
                            "content": content  # 保留代码内容
                        }
                    else:
                        preserved["component_content"] = {
                            "circular_ref": True,
                            "ref_path": visited[obj_id]
                        }

                    preserved["_circular_ref"] = True
                    preserved["_ref_path"] = visited[obj_id]
                    return preserved

                # 对于非顶层imports的循环引用，也保留基本结构
                if isinstance(obj, dict) and ("name" in obj or "id" in obj):
                    return {
                        "circular_ref": True,
                        "ref_path": visited[obj_id],
                        "name": obj.get("name", ""),
                        "id": obj.get("id", ""),
                        "type": obj.get("type", "")
                    }

                return {"circular_ref": True, "ref_path": visited[obj_id]}

            # 记录当前对象
            visited[obj_id] = path

            # 处理字典
            if isinstance(obj, dict):
                result = {}

                # 特殊处理dependencies字段，保留关键信息
                if path.endswith(".dependencies") and depth > max_depth:
                    # 对深层dependencies进行精简处理
                    simplified_deps = {}

                    for dep_type, dep_list in obj.items():
                        if isinstance(dep_list, list):
                            simplified_deps[dep_type] = []
                            for item in dep_list[:5]:  # 只保留前5个依赖项
                                if isinstance(item, dict):
                                    # 只保留关键标识字段
                                    simplified_item = {
                                        "id": item.get("id", ""),
                                        "name": item.get("name", ""),
                                        "type": item.get("type", ""),
                                        "file": item.get("file", ""),
                                        "simplified": True
                                    }
                                    simplified_deps[dep_type].append(simplified_item)

                    return simplified_deps

                # 正常处理字典中的每个键值对
                for key, value in obj.items():
                    result[key] = _remove_refs(value, depth + 1, f"{path}.{key}")
                return result

            # 处理列表
            elif isinstance(obj, list):
                result = []
                for i, item in enumerate(obj):
                    if i > 50:  # 列表长度限制
                        result.append({"truncated": True, "remaining_items": len(obj) - i})
                        break
                    result.append(_remove_refs(item, depth + 1, f"{path}[{i}]"))
                return result

            # 其他类型转为字符串
            return str(obj)

        # 开始处理
        return _remove_refs(data)

    def process_projects(self, projects_dir: Path):
        """处理目录中的所有项目"""
        if not projects_dir.exists():
            raise FileNotFoundError(f"项目目录不存在: {projects_dir}")

        projects = list(projects_dir.iterdir())
        self.stats.total_projects = len(projects)

        for project_path in tqdm(projects, desc="正在处理项目"):
            if project_path.is_dir():
                self.analyze_project(project_path)

        self._print_statistics()

    def _print_statistics(self):
        """打印处理统计信息"""
        print("\n处理完成！统计信息：")
        print(f"项目统计：")
        print(f"  总项目数: {self.stats.total_projects}")
        print(f"  成功处理: {self.stats.processed_projects}")
        print(f"  处理失败: {self.stats.failed_projects}")
        print(f"\n文件统计：")
        print(f"  总文件数: {self.stats.total_files}")
        print(f"  成功处理: {self.stats.processed_files}")
        print(f"  处理失败: {self.stats.failed_files}")

def main():
    parser = argparse.ArgumentParser(description='ArkTS项目代码分析工具')
    parser.add_argument('projects_dir', type=str, help='要分析的项目目录路径')
    parser.add_argument('--output-dir', type=str, default='./analysis_results',
                      help='分析结果输出目录（默认: ./analysis_results）')
    parser.add_argument('--log-dir', type=str, default='./logs',
                      help='日志文件目录（默认: ./logs）')

    args = parser.parse_args()
    
    try:
        projects_dir = Path(args.projects_dir)
        output_dir = Path(args.output_dir)
        log_dir = Path(args.log_dir)
        
        abstractor = ProjectAbstractor(output_dir, log_dir)
        abstractor.process_projects(projects_dir)
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())