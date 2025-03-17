from datetime import datetime
import shutil


SOURCE_FILE_DIR = '/Users/jiaoyiyang/harmonyProject/repos/singleFileProjects'
TARGET_DIR = '/Users/jiaoyiyang/harmonyProject/repos/mutationProjects'
import os
import random
from mergeCurrentFile import merge_ets_files

def get_ets_files(source_folder):
    # 获取源文件夹下所有子文件夹路径
    subfolders = [
        os.path.join(source_folder, folder)
        for folder in os.listdir(source_folder)
        if os.path.isdir(os.path.join(source_folder, folder))
    ]

    # 检查是否至少有两个子文件夹
    if len(subfolders) < 2:
        raise ValueError("源文件夹必须包含至少两个子文件夹")

    # 随机选取两个不同的子文件夹
    selected_subfolders = random.sample(subfolders, 2)

    # 收集所有ETS文件的绝对路径
    ets_files = []
    for subfolder in selected_subfolders:
        for root, _, files in os.walk(subfolder):
            for file in files:
                if file.endswith(".ets"):
                    ets_files.append(os.path.abspath(os.path.join(root, file)))

    name = generate_filename(ets_files[0], ets_files[1])
    new_folder_path, new_file_path = create_subfolder_and_file('/Users/jiaoyiyang/harmonyProject/repos/mutationProjects',name)
    for folder in selected_subfolders:
        copy_filtered_files(folder, new_folder_path)

    return ets_files , new_file_path

def generate_filename(ets1, ets2):
    folder1 = os.path.basename(os.path.dirname(ets1))[:8]  # 取前8个字符防过长
    folder2 = os.path.basename(os.path.dirname(ets2))[:8]
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{folder1}-{folder2}-{timestamp}"


def copy_filtered_files(src_dir, dest_dir):
    if not os.path.isdir(src_dir):
        print(f"源文件夹不存在: {src_dir}")
        return False

    src_name = os.path.basename(src_dir)

    # 创建目标目录
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 遍历源目录所有文件
    try:
        for current_path, _, filenames in os.walk(src_dir):
            # 计算相对路径
            relative_path = os.path.relpath(current_path, src_dir)
            target_path = os.path.join(dest_dir, relative_path)

            # 确保目标目录存在
            if not os.path.exists(target_path):
                os.makedirs(target_path)

            # 过滤并复制文件
            for filename in filenames:
                if (filename == src_name or
                        filename.startswith(src_name) or
                        filename.endswith('.ets')):
                    continue

                # 复制文件
                src_file = os.path.join(current_path, filename)
                dest_file = os.path.join(target_path, filename)
                shutil.copy2(src_file, dest_file)

        return True
    except Exception as e:
        print(f"复制失败: {str(e)}")
        return False

def create_subfolder_and_file(target_dir, file_name):
    subfolder_path = os.path.join(target_dir, file_name)
    file_path = os.path.join(subfolder_path, f"{file_name}.ets")

    # 创建子文件夹（如果不存在）
    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)

    # 创建ETS文件（如果不存在）
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('')  # 创建空文件

    return subfolder_path , file_path

if __name__ == "__main__":
    for i in range(20):
        selectedEts, targetFile = get_ets_files(SOURCE_FILE_DIR)
        merge_ets_files(selectedEts[0], selectedEts[1], targetFile)