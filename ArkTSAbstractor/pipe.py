from pathlib import Path
import logging
from typing import Optional

from projectAbstractor import ProjectAbstractor
from scripts.delete_test_files import delete_test_files
from codeClassifier import CodeClassifier
from addImport import process_directory as add_import_directory

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置路径
projects_dir = Path('/Users/liuxuejin/Downloads/gitee_cloned_repos_5min_stars')
project_output_dir = Path('./data/projects_abstracted')
log_dir = Path('./data/log')

def process_project(project_path: Path) -> bool:
    """处理单个项目"""
    try:
        # 分析项目
        project_abstractor = ProjectAbstractor(output_dir=project_output_dir, log_dir=log_dir)
        project_abstractor.analyze_project(project_path)
        
        # # 删除测试文件
        # delete_test_files(project_output_dir)
        #
        # # 分类代码
        # code_classifier = CodeClassifier(base_output_dir=project_output_dir)
        # code_classifier.classify_code(project_output_dir)
        #
        # # 添加导入
        # add_import_directory(project_output_dir)
        
        return True
    except Exception as e:
        logger.error(f"处理项目 {project_path} 时出错: {e}")
        return False

def main():
    try:
        # 确保输出目录存在
        project_output_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 处理所有项目
        success_count = 0
        total_count = 0
        
        for project_path in projects_dir.iterdir():
            if project_path.is_dir():
                total_count += 1
                if process_project(project_path):
                    success_count += 1
        
        logger.info(f"处理完成！成功: {success_count}/{total_count}")
        
    except Exception as e:
        logger.error(f"处理过程中出错: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())