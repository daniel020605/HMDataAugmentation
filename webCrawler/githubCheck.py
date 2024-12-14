import urllib.request
import json

#用于对检索到的仓库进行检查 检查方式为检查是否存在.ets文件

BASE_URL = "https://api.github.com"

# 设置请求头，包含 GitHub 的 Personal Access Token 进行身份验证
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Authorization': 'token your_token',  # todo: 替换为你的 GitHub token
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


# 获取仓库的默认分支
def get_default_branch(owner, repo):
    url = f"{BASE_URL}/repos/{owner}/{repo}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        return data['default_branch']  # 获取默认分支


# 获取仓库指定分支的最新提交 SHA
def get_latest_commit_sha(owner, repo, branch):
    url = f"{BASE_URL}/repos/{owner}/{repo}/branches/{branch}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        return data['commit']['sha']


# 获取仓库某个提交的文件树（目录结构）
def get_tree(owner, repo, sha):
    url = f"{BASE_URL}/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        return data['tree']  # 返回文件树


# 检查目录中是否包含 ets 文件夹
def check_for_ets_folder(owner, repo_url):
    try:
        # 从仓库 URL 获取仓库名称
        repo_name = repo_url.split('/')[-1].replace('.git', '')  # 从 URL 获取 repo 名称

        # 提取 owner 和 repo 名称
        owner = repo_url.split('/')[-2]

        # 获取默认分支
        branch = get_default_branch(owner, repo_name)

        # 获取最新 commit SHA
        sha = get_latest_commit_sha(owner, repo_name, branch)
        if sha:
            # 获取文件树
            tree = get_tree(owner, repo_name, sha)
            if tree:
                # 检查是否包含 ets 文件夹
                for file in tree:
                    if file['type'] == 'blob' and file['path'].endswith('.ets'):
                        print(repo_url + ' 包含 .ets 文件，为ArkTs代码，符合要求')
                        return True  # 找到 ets 文件夹，返回 True
                print(repo_url + ' 不包含 .ets 文件,不为ArkTS代码')
                return False  # 没有找到 ets 文件夹
            else:
                print(repo_url+'无法获取文件树')
                return False  # 无法获取文件树
        else:
            return False  # 无法获取最新 commit SHA
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


# 测试代码
if __name__ == '__main__':
    # 示例：检查某个仓库是否包含 ets 文件夹
    owner = "houseform"
    repo_url = "https://github.com/houseform/houseform.git"
    result = check_for_ets_folder(owner, repo_url)
    print(f"Does the repository contain 'ets' folder? {result}")