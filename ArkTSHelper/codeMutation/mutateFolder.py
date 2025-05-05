import os
import glob

from ArkTSHelper.codeMutation.singleFileMutate import process_single_ets_file


def generate_unique_folder(base_name, target_dir):
    """
    生成唯一递增文件夹名称
    :param base_name: 基础名称（如"0"）
    :param target_dir: 目标目录路径
    :return: 可用文件夹名称（如"0_3"）
    """
    counter = 1
    while True:
        new_name = f"{base_name}_{counter}"
        new_path = os.path.join(target_dir, new_name)
        if not os.path.exists(new_path):
            return new_name
        counter += 1


import os
import glob
import random


def process_source_folder(source_dir, target_dir, num_folders=2000):
    """主处理函数（随机选择指定数量的子文件夹）"""
    os.makedirs(target_dir, exist_ok=True)

    # 获取所有候选子文件夹
    all_folders = [
        f for f in os.listdir(source_dir)
        if os.path.isdir(os.path.join(source_dir, f))
    ]

    # 校验数量
    if len(all_folders) < num_folders:
        print(f"警告：请求处理 {num_folders} 个，但只有 {len(all_folders)} 个可用")
        num_folders = len(all_folders)

    # 随机选择不重复的文件夹
    selected_folders = random.sample(all_folders, num_folders)

    for folder in selected_folders:
        src_path = os.path.join(source_dir, folder)

        # 查找ETS文件（保持原有逻辑）
        ets_files = glob.glob(os.path.join(src_path, "*.ets"))
        if not ets_files:
            print(f"跳过 {folder}：无ETS文件")
            continue

        # 生成目标路径（保持原有逻辑）
        target_folder = generate_unique_folder(folder, target_dir)
        target_path = os.path.join(target_dir, target_folder)
        os.makedirs(target_path, exist_ok=True)

        new_filename = f"{target_folder}.ets"
        target_file = os.path.join(target_path, new_filename)

        # 处理文件内容（保持原有逻辑）
        try:
            processed = process_single_ets_file(ets_files[0])
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(processed)
            print(f"成功生成：{target_folder}/{new_filename}")
        except Exception as e:
            print(f"处理失败 [{folder}]: {str(e)}")


if __name__ == "__main__":
    SOURCE = "/Users/jiaoyiyang/harmonyProject/repos/combined_collected"  # 修改为源路径
    TARGET = "/Users/jiaoyiyang/harmonyProject/repos/mutated_projects"  # 修改为目标路径

    process_source_folder(SOURCE, TARGET)