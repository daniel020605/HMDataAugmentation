import os
import shutil
import pypinyin


def convert_chinese_to_pinyin(folder_path):
    """将文件夹名中的中文字符替换为拼音首字母。"""
    def is_chinese(char):
        return '\u4e00' <= char <= '\u9fff'

    def contains_chinese(s):
        return any(is_chinese(char) for char in s)

    def to_pinyin_first_letter(name):
        return ''.join(pypinyin.lazy_pinyin(name, style=pypinyin.Style.FIRST_LETTER))

    for root, dirs, _ in os.walk(folder_path, topdown=True):
        for dir_name in dirs:
            if contains_chinese(dir_name):
                old_dir_path = os.path.join(root, dir_name)
                new_dir_name = to_pinyin_first_letter(dir_name)
                new_dir_path = os.path.join(root, new_dir_name)
                if not os.path.exists(new_dir_path):
                    os.rename(old_dir_path, new_dir_path)
                    print(f"Renamed: {old_dir_path} -> {new_dir_path}")
                else:
                    print(f"Skipping: {new_dir_path} already exists.")


def copy_folders_with_files(source_directory, target_directory):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    counter = {}

    def folder_contains_files(folder_path):
        build_profile_path = os.path.join(folder_path, 'build-profile.json5')
        hvigorfile_path = os.path.join(folder_path, 'hvigorfile.ts')
        return os.path.isfile(build_profile_path) and os.path.isfile(hvigorfile_path)

    def get_unique_target_path(base_name, counter, target_directory):
        if base_name not in counter:
            counter[base_name] = 1
        else:
            counter[base_name] += 1

        while True:
            target_path = os.path.join(target_directory, f"{base_name}_{counter[base_name]}")
            if not os.path.exists(target_path):
                return target_path
            counter[base_name] += 1

    def process_folder(folder_path, target_directory, counter):
        dir_name = os.path.basename(folder_path)
        target_path = get_unique_target_path(dir_name, counter, target_directory)
        try:
            shutil.copytree(folder_path, target_path, dirs_exist_ok=True)
            print(f"Copied {folder_path} to {target_path}")
        except Exception as e:
            print(f"Error copying {folder_path}: {e} -- Skipping this directory.")

    def recursive_search(current_directory, target_directory, counter):
        for dir_name in os.listdir(current_directory):
            dir_path = os.path.join(current_directory, dir_name)
            if os.path.isdir(dir_path):
                if folder_contains_files(dir_path):
                    try:
                        process_folder(dir_path, target_directory, counter)
                    except Exception as e:
                        print(f"Error processing folder {dir_path}: {e} -- Skipping.")
                else:
                    try:
                        recursive_search(dir_path, target_directory, counter)
                    except Exception as e:
                        print(f"Error in recursive search for {dir_path}: {e} -- Skipping.")

    recursive_search(source_directory, target_directory, counter)


def collect_repo_and_project_names(source_directory, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        def folder_contains_files(folder_path):
            build_profile_path = os.path.join(folder_path, 'build-profile.json5')
            hvigorfile_path = os.path.join(folder_path, 'hvigorfile.ts')
            return os.path.isfile(build_profile_path) and os.path.isfile(hvigorfile_path)

        def recursive_search(repo_name, current_directory):
            counter = 1
            for dir_name in os.listdir(current_directory):
                dir_path = os.path.join(current_directory, dir_name)
                if os.path.isdir(dir_path):
                    try:
                        if folder_contains_files(dir_path):
                            file.write(f"仓库名: {repo_name}, 项目名: {dir_name}\n")
                            print(f"Found matching project in {repo_name}: {dir_name}")
                            counter += 1
                        else:
                            recursive_search(repo_name, dir_path)
                    except FileNotFoundError as e:
                        print(f"Skipping {dir_path}: {e}")
                    except Exception as e:
                        print(f"Error with {dir_path}: {e}")

        def process_repo(repo_path):
            repo_name = os.path.basename(repo_path)
            recursive_search(repo_name, repo_path)

        for repo_name in os.listdir(source_directory):
            repo_path = os.path.join(source_directory, repo_name)
            if os.path.isdir(repo_path):
                process_repo(repo_path)

if __name__ == "__main__":
    source_directory = r'C:\Users\sunguyi\Desktop\repos\gitee_cloned_repos_5min_stars'
    target_directory = r'C:\Users\sunguyi\Desktop\repos\gitee_5min_stars_projects'
    copy_folders_with_files(source_directory, target_directory)
    convert_chinese_to_pinyin(target_directory)
    # source_directory = r'C:\Users\sunguyi\Desktop\repos\github_cloned_repos_1min_stars'  # 替换为你的根目录路径，其中包含多个仓库
    # output_file = 'output.txt'  # 替换为你希望存储结果的txt文件路径
    # collect_repo_and_project_names(source_directory, output_file)


