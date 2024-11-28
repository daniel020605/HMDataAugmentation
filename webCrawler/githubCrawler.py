import time
from urllib.request import urlopen
from urllib.request import Request
import json
import urllib.parse  # 导入 URL 编码库

from webCrawler.githubCheck import check_for_ets_folder


# 定义获取结果的函数
def get_results(search, headers, page, pageSize, minStars, latestPushTime):
    # 对搜索条件进行 URL 编码，确保 URL 中的中文和空格被正确转义
    encoded_search = urllib.parse.quote(search)  # 对搜索字符串进行编码
    encoded_latest_time = urllib.parse.quote(latestPushTime)
    # 构造 GitHub API 的请求 URL
    url = f'https://api.github.com/search/repositories?q={encoded_search}%20stars:>={minStars}%20pushed:>={encoded_latest_time}&page={page}&per_page={pageSize}&sort=stars&order=desc'

    # 创建请求对象
    req = Request(url, headers=headers)
    response = urlopen(req).read()  # 发送请求并读取响应
    result = json.loads(response.decode())  # 将响应解析为 JSON 格式
    return result  # 返回解析后的结果


if __name__ == '__main__':
    # 指定 TypeScript 语言的搜索关键词
    search = 'language:typescript (鸿蒙 OR arkts OR ArkTS OR harmony OR Harmony)'  # 需要对搜索关键词进行编码

    # 设置请求头，包含 GitHub 的 Personal Access Token 进行身份验证
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Authorization': 'token your_token',  #todo: 替换为你的 GitHub token
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    repos_list = []
    stars_list = []

    page = 1  # 从第1页开始
    pageSize = 50
    minStars = 5
    latestPushTime = '2021-06-02'

    while True:
        # 获取当前页的数据
        results = get_results(search, headers, page, pageSize, minStars, latestPushTime)

        if not results['items']:  # 如果没有仓库返回，停止爬取
            break

        # 遍历当前页的每个仓库
        for item in results['items']:
            # 将仓库的编号、名称和克隆 URL 保存到 repos_list 中
            repos_list.append([item["name"], item["clone_url"]])
            stars_list.append(item["stargazers_count"])  # 保存仓库的星标数


        print(f"Page {page} has {len(results['items'])} repositories.")  # 打印当前页的仓库数量

        page += 1  # 请求下一页

        time.sleep(1)  # 适当休眠，避免请求过于频繁

    print(f"Total page {page - 1} has {len(repos_list)}")
    with open("./ArkTsReposOnGithub.txt", "w", encoding="utf-8") as f:
        count = 1
        for i in range(len(repos_list)):
            print(repos_list[i][1])
            if check_for_ets_folder(repos_list[i][0], repos_list[i][1]):
                f.write(f"{count},{repos_list[i][0]},{repos_list[i][1]}\n")
                count += 1

    print(f"Total repositories fetched: {len(repos_list)}")