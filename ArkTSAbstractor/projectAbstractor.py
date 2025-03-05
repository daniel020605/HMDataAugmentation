import os
import json
from tqdm import tqdm

from ArkTSAbstractor.fileAnalyzer import analyze_ets_file
from importAnalyzer import analyze_imports

def get_ets_files(project_path):
    ets_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.ets'):
                ets_files.append(os.path.join(root, file))
    return ets_files

def analyze_ets_project(project_path):
    project_name = os.path.basename(project_path)
    output_folder = './analysis_results'
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f'{project_name}.json')

    ets_files = get_ets_files(project_path)
    project_analysis = []

    for file_path in ets_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                file_content = file.read()
                analysis = analyze_ets_file(file_content)
                project_analysis.append({
                    'file': file_path,
                    'file_type': analysis.file_type,
                    'ui_code': analysis.ui_code,
                    'variables': analysis.variables,
                    'functions': analysis.functions
                })
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(project_analysis, json_file, indent=4, ensure_ascii=False)
    # Log the processed project
    with open('processed_projects.log', 'a', encoding='utf-8') as log_file:
        log_file.write(f"{project_name}\n")

def process_projects(projects_path):
    for project in tqdm(os.listdir(projects_path)):
        project_path = os.path.join(projects_path, project)
        analyze_ets_project(project_path)

if __name__ == '__main__':

    projects_path = '/Users/liuxuejin/Downloads/gitee_cloned_repos_5min_stars'
    process_projects(projects_path)
    projects_path = '/Users/liuxuejin/Downloads/github_cloned_repos_1min_stars'
    process_projects(projects_path)

    # project_path = '/Users/liuxuejin/Downloads/github_cloned_repos_1min_stars/harmony-netease'
    # analyze_ets_project(project_path)

    # project_path = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/test'
    # analyze_ets_project(project_path)