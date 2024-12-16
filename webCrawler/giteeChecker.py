import urllib.request
import json
from os import access

# Gitee API 基础 URL
BASE_URL = "https://gitee.com/api/v5"

# 设置请求头，包含 Gitee 的身份验证信息
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

# Gitee access_token
access_token = ""  # todo: 替换为自己的 token


# 获取仓库的最后更新分支
def get_latest_branch(owner, repo):
    # 构建获取分支的请求 URL，按更新时间排序
    url = f"{BASE_URL}/repos/{owner}/{repo}/branches?access_token={access_token}&sort=updated&direction=desc&page=1"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        if data:
            return data[0]['name']  # 返回最新更新的分支名称
        else:
            return None  # 如果没有分支数据，返回 None


# 获取仓库某个提交的文件树（目录结构）
def get_tree(owner, repo, sha):
    url = f"{BASE_URL}/repos/{owner}/{repo}/git/trees/{sha}?access_token={access_token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        return data['tree']


# 检查目录中是否包含 .ets 文件
def check_for_ets_folder(repo_url):
    try:
        # 从仓库 URL 获取仓库名称
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        owner = repo_url.split('/')[-2]
        branch = get_latest_branch(owner, repo_name)


        if branch:
            # 获取文件树
            tree = get_tree(owner, repo_name, branch)
            if tree:
                for file in tree:
                    if check_for_ets_file(file):
                        print(repo_url + " 包含 .ets 文件，符合要求")
                        return True
                print("没有找到 .ets 文件")
                return False
            else:
                print("无法获取文件树")
                return False
        else:
            print("无法获取最新 commit的branch")
            return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False  # 出现错误时，返回 False


def check_for_ets_file(file):
    try:
        # 遍历文件树
        if file['type'] == 'blob' and file['path'].endswith('.ets'):
            print(f"找到 .ets 文件: {file['path']}")
            return True  # 找到 .ets 文件，返回 True
        elif file['type'] == 'tree':
            # 如果是目录类型，递归调用检查
            # 通过 url 获取子目录的文件树
            url = file['url']
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                tree = data['tree']
                # 递归检查该目录下的所有文件
                for sub_file in tree:
                    if check_for_ets_file(sub_file):
                        return True
    except Exception as e:
        print(f"An error occurred while checking {file['path']}: {str(e)}")
    return False  # 如果没有找到 .ets 文件，返回 False

# 测试函数
if __name__ == '__main__':
    # 测试仓库 URL
    repo_url = "https://gitee.com/harmonyos/codelabs"
    result = check_for_ets_folder(repo_url)
    print(f"仓库 {repo_url} 是否包含 .ets 文件？{result}")

