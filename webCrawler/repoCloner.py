import os
import subprocess
import threading

def clone_repo(repo_name, repo_url, target_path, timeout):
    try:
        print(f"正在克隆仓库: {repo_name} ({repo_url})")
        process = subprocess.Popen(["git", "clone", repo_url, target_path])
        process.wait(timeout=timeout)
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
        return True
    except subprocess.TimeoutExpired:
        print(f"克隆超时: {repo_name} ({repo_url})")
        process.terminate()  # Terminate the subprocess
        process.wait()  # Wait for the subprocess to terminate
    except Exception as e:
        print(f"克隆失败: {repo_name} ({repo_url})，错误信息: {e}")
        process.terminate()  # Terminate the subprocess
        process.wait()  # Wait for the subprocess to terminate
    return False

def clone_repos(file_path, clone_directory, timeout=300):
    """
    克隆 Gitee 仓库列表到指定目录。

    参数：
    file_path (str): 包含仓库信息的文件路径。
    clone_directory (str): 克隆目标路径。
    timeout (int): 克隆超时时间（秒）。
    """
    # 创建存储仓库的目录
    os.makedirs(clone_directory, exist_ok=True)

    # 读取文件并解析
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()  # 先读取所有行

    cloned_count = 0

    def clone_and_update(line_index, repo_id, repo_name, repo_url):
        nonlocal cloned_count
        # 检查目标是否存在同名仓库
        target_path = os.path.join(clone_directory, repo_name)
        counter = 1
        while os.path.exists(target_path):
            target_path = os.path.join(clone_directory, f"{repo_name}_{counter}")
            counter += 1

        if clone_repo(repo_name, repo_url, target_path, timeout):
            lines[line_index] = f"{repo_id},{repo_name},{repo_url},1\n"
            with open(file_path, "w", encoding="utf-8") as file:
                file.writelines(lines)
            cloned_count += 1

    threads = []
    for line_index, line in enumerate(lines):
        if len(line.strip()) == 0 or line.startswith("#"):
            continue
        try:
            # 按逗号分割，提取仓库名称和链接
            repo_id, repo_name, repo_url, cloned = line.strip().split(",")

            if cloned == "0":
                thread = threading.Thread(target=clone_and_update, args=(line_index, repo_id, repo_name, repo_url))
                threads.append(thread)
                thread.start()

        except Exception as e:
            print(f"处理失败: {line.strip()}，错误信息: {e}")

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print(f"克隆完成。本次共克隆了 {cloned_count} 个仓库。")