import os
import subprocess
import requests

from AndroidHelper.UIGetter import get_UI
from AndroidHelper.codeChecker import check_and_build_android_project
from AndroidHelper.projectAnalyser import extract_functions_from_project, save_functions_to_json
from AndroidHelper.projectPreprocessor import gradle_source_replace

import configparser

config = configparser.ConfigParser()
config.read("../secret.properties")

GITHUB_TOKEN = config.get("DEFAULT", "GITHUB_API_KEY")

def read_repos(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def clone_repo(repo_url, clone_path):
    try:
        if not os.path.exists(clone_path):
            os.makedirs(clone_path, exist_ok=True)

        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        repo_name = repo_url.split('/')[-1]
        api_url = f'https://api.github.com/repos/{repo_url.split("/")[-2]}/{repo_name}/tarball'
        response = requests.get(api_url, headers=headers, stream=True)
        response.raise_for_status()

        tarball_path = f'{clone_path}.tar.gz'
        with open(tarball_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        subprocess.run(['tar', '-xzf', tarball_path, '--strip-components=1', '-C', clone_path], check=True)
        os.remove(tarball_path)
    except (requests.RequestException, subprocess.CalledProcessError) as e:
        print(f"Error cloning {repo_url}: {e}")

def run_pipeline(clone_path):
    try:
        project_name = clone_path.split('/')[-1]
        project_path = "/Users/daniel/Desktop/Android/" + project_name
        output_path = f"./functions/{project_name}.json"
        UI_path = "./UI/"

        # 任务列表
        # gradle_source_replace(project_path)
        # check_and_build_android_project(project_path)
        get_UI(project_path, UI_path)
        # functions_dict = extract_functions_from_project(project_path)
        # save_functions_to_json(functions_dict, output_path)
    except Exception as e:
        print(f"Error running pipeline in {clone_path}: {e}")

def delete_repo(clone_path):
    try:
        if os.path.exists(clone_path):
            subprocess.run(['rm', '-rf', clone_path], check=True)
        else:
            print(f"Path {clone_path} does not exist, skipping deletion.")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting {clone_path}: {e}")

def main():
    repos = read_repos('extracted_urls.txt')
    for repo_url in repos:
        repo_name = repo_url.split('/')[-1]
        clone_path = os.path.join("/Users/daniel/Desktop/Android/", repo_name)
        output_path = f"./functions/{repo_name}.json"

        # 重复检查
        # if os.path.exists(output_path):
        #     print(f"Output for {repo_name} already exists, skipping.")
        #     continue

        try:
            clone_repo(repo_url, clone_path)
            run_pipeline(clone_path)
        except Exception as e:
            print(f"Error processing {repo_url}: {e}")
        finally:
            delete_repo(clone_path)

if __name__ == "__main__":
    main()