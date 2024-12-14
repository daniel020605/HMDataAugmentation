import os
import subprocess

# 文件路径
file_path = "ArkTsReposOnGithub.txt"

# 克隆目标路径
clone_directory = "github_cloned_repos"

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

        # 克隆命令
        if cloned == "0":  # 这里注意 `cloned` 是字符串，需要与 "0" 比较
            print(f"正在克隆仓库: {repo_name} ({repo_url})")
            subprocess.run(["git", "clone", repo_url, os.path.join(clone_directory, repo_name)], check=True)

            # 克隆完成后更新状态为1
            lines[line_index] = f"{repo_id},{repo_name},{repo_url},1\n"

            # 立即写回更新的行
            with open(file_path, "w", encoding="utf-8") as file:
                file.writelines(lines)

    except Exception as e:
        print(f"克隆失败: {line.strip()}，错误信息: {e}")

print("克隆完成。")
