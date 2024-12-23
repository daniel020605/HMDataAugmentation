import os
import shutil
import stat

def remove_folders_without_ets(parent_folder):
    deleted_count = 0
    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.isdir(folder_path):
            contains_ets = False
            try:
                for root, dirs, files in os.walk(folder_path):
                    if any(file.endswith('.ets') for file in files):
                        contains_ets = True
                        break
            except PermissionError:
                print(f"拒绝访问: {folder_path}")
                continue

            if not contains_ets:
                try:
                    # Change the permissions of the directory
                    os.chmod(folder_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    shutil.rmtree(folder_path)
                    deleted_count += 1
                    print(f"删除文件夹: {folder_path}")
                except PermissionError:
                    print(f"无法删除文件夹: {folder_path}，权限被拒绝")
                except Exception as e:
                    print(f"删除文件夹时出错: {folder_path}，错误: {e}")
    print(f"总共删除了 {deleted_count} 个文件夹")