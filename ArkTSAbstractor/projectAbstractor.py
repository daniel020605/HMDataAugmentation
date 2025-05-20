import os
import json
from tqdm import tqdm
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

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

            if project_analysis:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(project_analysis, f, indent=4, ensure_ascii=False)
                
                with open(self.log_dir / 'processed_projects.log', 'a', encoding='utf-8') as f:
                    f.write(f"{project_name}\n")
                
                self.stats.processed_projects += 1
                return True

        except Exception as e:
            self.file_logger.error(f"处理项目 {project_path} 时出错: {e}")
            self.stats.failed_projects += 1
        return False

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