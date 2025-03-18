#!/usr/bin/env python3
import os
import argparse

def delete_test_files(directory):
    """
    删除指定目录下所有文件名中包含.test的文件
    
    Args:
        directory (str): 要处理的目录路径
    """
    # 确保目录存在
    if not os.path.exists(directory):
        print(f"错误：目录 '{directory}' 不存在")
        return

    # 统计删除的文件数量
    deleted_count = 0

    # 遍历目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if '.test' in file:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"已删除: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"删除文件 '{file_path}' 时出错: {str(e)}")

    print(f"\n总共删除了 {deleted_count} 个文件")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='删除指定目录下所有包含.test的文件')
    parser.add_argument('directory', help='要处理的目录路径')
    parser.add_argument('--dry-run', action='store_true', help='仅显示要删除的文件，不实际删除')

    args = parser.parse_args()

    if args.dry_run:
        print("模拟运行模式 - 将显示要删除的文件但不会实际删除：\n")
        for root, dirs, files in os.walk(args.directory):
            for file in files:
                if '.test' in file:
                    print(f"将要删除: {os.path.join(root, file)}")
    else:
        delete_test_files(args.directory)

if __name__ == "__main__":
    main() 