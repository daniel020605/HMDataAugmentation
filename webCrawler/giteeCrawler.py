import time
from urllib.request import urlopen
from urllib.request import Request
import json
import urllib.parse  # 导入 URL 编码库

# 定义获取结果的函数
def get_results(search, headers, page):
    # 对搜索条件进行 URL 编码，确保 URL 中的中文和空格被正确转义
    encoded_search = urllib.parse.quote(search)  # 对搜索字符串进行编码

    # 构造 Gitee API 的请求 URL
    url = f'https://gitee.com/api/v5/search/repositories?q=arkts&page=1&per_page=20&language=TypeScript&sort=stars_count&order=desc'

    # 创建请求对象
    req = Request(url, headers=headers)
    try:
        response = urlopen(req).read()  # 发送请求并读取响应
        result = json.loads(response.decode())  # 将响应解析为 JSON 格式
        return result  # 返回解析后的结果
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


if __name__ == '__main__':
    # 指定 TypeScript 语言的搜索关键词
    search = 'a'

    # 设置请求头，包含 Gitee 的 Personal Access Token 进行身份验证
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Authorization': 'token your_token',  # todo:替换为你的 Gitee token
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    count = 1  # 用来编号每个仓库

    repos_list = []  # 存储仓库的信息
    stars_list = []  # 存储每个仓库的星标数

    page = 1  # 从第1页开始
    while page == 1:
        # 获取当前页的数据
        results = get_results(search, headers, page)

        if not results:  # 如果没有仓库返回，停止爬取
            break

        # 遍历当前页的每个仓库
        for item in results['data']:  # 'data' 是 Gitee API 返回的数据字段
            # 将仓库的编号、名称和克隆 URL 保存到 `repos_list` 中
            repos_list.append([count, item["name"], item["html_url"]])  # 'html_url' 是 Gitee 仓库的 URL
            stars_list.append(item["star_count"])  # 保存仓库的星标数，字段是 'star_count'
            count += 1  # 仓库编号自增

        print(f"Page {page} has {len(results['data'])} repositories.")  # 打印当前页的仓库数量

        page += 1  # 请求下一页

        time.sleep(1)  # 适当休眠，避免请求过于频繁

    # 将所有结果保存到文件中
    with open("./ArkTsReposOnGitee.txt", "w", encoding="utf-8") as f:
        for i in range(len(repos_list)):
            # 将仓库编号、名称和克隆 URL 以逗号分隔保存到文件
            f.write(f"{repos_list[i][0]},{repos_list[i][1]},{repos_list[i][2]}\n")

    print(f"Total repositories fetched: {len(repos_list)}")  # 打印总共抓取到的仓库数量