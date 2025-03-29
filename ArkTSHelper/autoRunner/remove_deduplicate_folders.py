import os
import re
import hashlib
import shutil
from pathlib import Path


def get_folder_key(folder_name):
    """解析文件夹名称，返回(前缀, 序号)元组"""
    # 匹配形如 "name" 或 "name_123" 的格式
    match = re.match(r"^(.+?)(_(\d+))?$", folder_name)
    prefix = match.group(1)
    number = int(match.group(3)) if match.group(3) else 0
    return (prefix, number)


def file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def deduplicate_folders(root_dir):
    """主去重逻辑"""
    # 数据结构：{(前缀, 文件哈希): [文件夹列表]}
    groups = {}

    # 第一遍扫描：建立分组索引
    for folder in Path(root_dir).iterdir():
        if not folder.is_dir():
            continue

        # 解析文件夹名称
        prefix, number = get_folder_key(folder.name)

        # 查找对应的ets文件
        ets_file = folder / f"{prefix}.ets"
        if not ets_file.exists():
            continue

        # 计算文件哈希
        file_id = file_hash(ets_file)

        # 更新分组字典
        key = (prefix, file_id)
        if key not in groups:
            groups[key] = []
        groups[key].append((number, folder))

    # 第二遍处理：执行删除操作
    for (prefix, _), folders in groups.items():
        # 按序号排序（从小到大）
        sorted_folders = sorted(folders, key=lambda x: x[0])

        # 保留第一个（序号最小），其余标记删除
        keep_folder = sorted_folders[0][1]
        print(f"\n保留组 [{prefix}]: {keep_folder.name}")

        for number, folder in sorted_folders[1:]:
            print(f"删除重复项: {folder.name} (序号 {number})")
            # 实际删除前建议先注释下一行，测试输出
            shutil.rmtree(folder)


if __name__ == "__main__":
    target_dir = "/Users/jiaoyiyang/harmonyProject/repos/newExtracted"  # 修改为实际路径
    deduplicate_folders(target_dir)