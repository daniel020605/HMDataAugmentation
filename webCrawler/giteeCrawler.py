import requests

from webCrawler.giteeChecker import check_for_ets_folder
from webCrawler.remove_folders_without_ets import remove_folders_without_ets
from webCrawler.repoCloner import clone_repos


def extract_repo_data(api_url, minStars):
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        # 提取每个仓库的数据
        repo_data = []
        for hit in data['hits']['hits']:
            repo = hit['fields']
            star_count = repo['count.star'][0]

            # 如果仓库的 Star 数低于 minStars，则跳过
            if star_count < minStars:
                continue

            repo_info = {
                'repo_name': repo['title'][0],  # 仓库名
                'star_count': star_count,  # Star 数
                'repo_url': repo['url'][0],  # 仓库地址
                'last_push_time': repo['last_push_at'][0]  # 最后一次提交时间
            }
            repo_data.append(repo_info)

        return repo_data
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return None


def search_multiple_keywords(keywords, minStars):
    base_url = "https://api.indexea.com/v1/search/widget/wjawvtmm7r5t25ms1u3d?"

    all_repos = set()  # 使用集合去重仓库 URL
    results = []  # 用于存储最终去重和排序后的仓库列表

    # 循环多个关键词
    for keyword in keywords:
        print(f"搜索关键词：{keyword}")

        page = 0  # 从第 0 页开始
        while True:
            # 构建搜索 URL，分页从 0 开始
            search_url = f"{base_url}query=1048&q={keyword}&from={page * 20}&size=20&编程语言=TypeScript&sort_by_f=Star%20%E6%95%B0"
            print(f"请求 URL: {search_url}")

            # 提取该关键词搜索的仓库数据
            repos = extract_repo_data(search_url, minStars)

            # 如果当前页面没有满足条件的仓库，停止分页
            if not repos:
                break

            # 将每个仓库 URL 加入集合，避免重复
            for repo in repos:
                if repo['repo_url'] not in all_repos:
                    all_repos.add(repo['repo_url'])
                    results.append(repo)

            page += 1  # 请求下一页
            print("-" * 50)

    # 根据 Star 数进行降序排序
    results.sort(key=lambda x: x['star_count'], reverse=True)

    # 打印最终的去重且排序后的仓库信息
    print(f"共找到 {len(results)} 个符合要求的仓库（去重后）：")
    return results



if __name__ == "__main__":
    # 关键词列表，可以修改为你需要的多个关键词
    keywords = ["Harmony", "HarmonyOS", "OpenHarmony", "鸿蒙", "ArkTs", "harmony", "arkts"]
    minStars = 1  # 设置最小星标数
    file_path = f"./ArkTsReposOnGitee_{minStars}stars.txt"

    # 检查文件是否已经完成列表获取
    file_completed = False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines and lines[0].strip() == "# COMPLETED":
                file_completed = True
                print("文件已完成列表获取。")
    except FileNotFoundError:
        pass

    if not file_completed:
        # 搜索并提取数据
        results = search_multiple_keywords(keywords, minStars)
        with open(file_path, "w", encoding="utf-8") as f:
            count = 1
            for repo in results:
                print(
                    f"仓库名: {repo['repo_name']}, Star 数: {repo['star_count']}, 地址: {repo['repo_url']}, 最后一次提交时间: {repo['last_push_time']}"
                )
                f.write(f"{count},{repo['repo_name']},{repo['repo_url']},0\n")
                count += 1

        # 在第一行加上#COMPLETED
        with open(file_path, "r+", encoding="utf-8") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(f"# COMPLETED\n" + content)

    clone_directory = f"gitee_cloned_repos_{minStars}min_stars"
    clone_repos(file_path, clone_directory)
    remove_folders_without_ets(clone_directory)

