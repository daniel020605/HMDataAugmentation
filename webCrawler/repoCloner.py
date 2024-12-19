import os
import subprocess

def clone_repos(file_path, clone_directory):
    """
    克隆 Gitee 仓库列表到指定目录。

    参数：
    file_path (str): 包含仓库信息的文件路径。
    clone_directory (str): 克隆目标路径。
    """
    # 创建存储仓库的目录
    os.makedirs(clone_directory, exist_ok=True)

    # 读取文件并解析
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()  # 先读取所有行

    for line_index, line in enumerate(lines):
        if len(line.strip()) == 0 or line.startswith("#"):
            continue
        try:
            # 按逗号分割，提取仓库名称和链接
            repo_id, repo_name, repo_url, cloned = line.strip().split(",")

            if cloned == "0":
                print(f"正在克隆仓库: {repo_name} ({repo_url})")

                # 检查目标目录是否存在同名仓库
                target_path = os.path.join(clone_directory, repo_name)
                counter = 1
                while os.path.exists(target_path):
                    target_path = os.path.join(clone_directory, f"{repo_name}_{counter}")
                    counter += 1

                # 克隆仓库
                subprocess.run(["git", "clone", repo_url, target_path], check=True)

                # 克隆完成后更新状态为 1
                lines[line_index] = f"{repo_id},{repo_name},{repo_url},1\n"

                # 立即写回更新的行
                with open(file_path, "w", encoding="utf-8") as file:
                    file.writelines(lines)

        except Exception as e:
            print(f"克隆失败: {line.strip()}，错误信息: {e}")

    print("克隆完成。")


