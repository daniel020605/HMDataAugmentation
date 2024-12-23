import time
from urllib.request import urlopen
from urllib.request import Request
import json
import urllib.parse

from webCrawler.githubChecker import check_for_ets_folder
from webCrawler.remove_folders_without_ets import remove_folders_without_ets
from webCrawler.repoCloner import clone_repos


# 定义获取结果的函数
def get_results(search, headers, page, pageSize, minStars, latestPushTime):
    # 对搜索条件进行 URL 编码，确保 URL 中的中文和空格被正确转义
    encoded_search = urllib.parse.quote(search)
    encoded_latest_time = urllib.parse.quote(latestPushTime)
    # 构造 GitHub API 的请求 URL
    url = f'https://api.github.com/search/repositories?q={encoded_search}%20stars:>={minStars}%20pushed:>={encoded_latest_time}&page={page}&per_page={pageSize}&sort=stars&order=desc'

    # 创建请求对象
    req = Request(url, headers=headers)
    response = urlopen(req).read()
    result = json.loads(response.decode())
    return result

def get_repos_list(search, headers, page, pageSize, minStars, latestPushTime):
    while True:
        # 获取当前页的数据
        results = get_results(search, headers, page, pageSize, minStars, latestPushTime)

        if not results['items']:
            break

        for item in results['items']:
            repos_list.append([item["name"], item["clone_url"]])
        page += 1

        time.sleep(1)  # 适当休眠，避免请求过于频繁

    print(f"符合筛选要求的仓库数为：{len(repos_list)}")

    return repos_list


if __name__ == '__main__':
    # 指定搜索关键词
    search = 'language:typescript (鸿蒙 OR arkts OR ArkTS OR harmony OR Harmony)'
    page = 1
    pageSize = 50
    minStars = 1
    latestPushTime = '2021-01-01'

    # 设置请求头，包含 GitHub 的 Personal Access Token 进行身份验证
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Authorization': 'token your_token',  #todo: 替换为你的 GitHub token
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    repos_list = []  # 存储仓库数据
    file_path = f"./ArkTsReposOnGithub_{minStars}stars.txt"

    # 检查文件是否已经完成列表获取
    file_completed = False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines and lines[0].strip().startswith("# COMPLETED"):
                file_completed = True
                print("文件已完成列表获取。")
    except FileNotFoundError:
        pass

    if not file_completed:
        repos_list = get_repos_list(search, headers, page, pageSize, minStars, latestPushTime)
        with open(file_path, "w", encoding="utf-8") as f:
            count = 1
            for i in range(len(repos_list)):
                if check_for_ets_folder(repos_list[i][0], repos_list[i][1]):
                    f.write(f"{count},{repos_list[i][0]},{repos_list[i][1]},0\n")
                    count += 1

        # 在第一行加上#COMPLETED
        with open(file_path, "r+", encoding="utf-8") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(f"# COMPLETED - minStars: {minStars}, latestPushTime: {latestPushTime}\n" + content)

        print(f"符合筛选要求的仓库数为：{count}")

    clone_directory = f"github_cloned_repos_{minStars}min_stars"
    clone_repos(file_path, clone_directory)
    remove_folders_without_ets(clone_directory)