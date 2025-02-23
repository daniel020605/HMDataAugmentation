import os
import json5
import shutil

def find_folders_without_compatible_sdk_version(root_dir):
    folders_to_delete = []
    # 列出根目录下的所有一级子文件夹
    for sub_dir in os.listdir(root_dir):
        sub_dir_path = os.path.join(root_dir, sub_dir)
        if os.path.isdir(sub_dir_path):
            file_path = os.path.join(sub_dir_path, "build-profile.json5")
            if os.path.isfile(file_path):
                try:
                    # 读取并解析 JSON5 文件
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json5.load(f)
                    # 递归检查是否存在 compatibleSdkVersion 字段
                    if not has_compatible_sdk_version(data):
                        folders_to_delete.append(sub_dir_path)
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")
    return folders_to_delete

def has_compatible_sdk_version(data):
    # 如果当前层级有 compatibleSdkVersion 字段，返回 True
    if isinstance(data, dict):
        if "compatibleSdkVersion" in data:
            return True
        # 递归检查嵌套的字典或列表
        for key, value in data.items():
            if has_compatible_sdk_version(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if has_compatible_sdk_version(item):
                return True
    return False

def delete_folders(folders):
    deleted_count = 0
    for folder in folders:
        try:
            # 使用 shutil.rmtree 删除整个目录树
            if os.path.isdir(folder):
                shutil.rmtree(folder)
                print(f"删除文件夹: {folder}")
                deleted_count += 1
        except Exception as e:
            print(f"删除文件夹 {folder} 失败: {e}")
    return deleted_count

def main():
    # 设置根目录
    root_dir = "C:/Users/sunguyi/Desktop/repos/gitee_5min_stars_projects"

    # 查找所有没有 compatibleSdkVersion 字段的文件夹
    folders_to_delete = find_folders_without_compatible_sdk_version(root_dir)

    # 删除这些文件夹并统计删除数量
    deleted_count = delete_folders(folders_to_delete)

    print(f"总共删除了 {deleted_count} 个文件夹。")

if __name__ == "__main__":
    main()