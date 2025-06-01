import json
import requests
import os
from urllib.parse import urlparse

# 创建存储HTML的目录
output_dir = "html_pages"
os.makedirs(output_dir, exist_ok=True)

def get_filename_from_url(url):
    """从URL生成安全的文件名"""
    parsed = urlparse(url)
    path = parsed.path.strip('/').replace('/', '_')
    return f"{parsed.netloc}_{path}.html" if path else f"{parsed.netloc}.html"

# 新增辅助函数
def is_document_visited(object_id):
    """检查文档是否已被访问"""
    visited_file = os.path.join(output_dir, 'visited_documents.json')
    if not os.path.exists(visited_file):
        return False
    with open(visited_file, 'r', encoding='utf-8') as f:
        visited = json.load(f)
    return object_id in visited

def mark_document_as_visited(object_id, url):
    """标记文档为已访问"""
    visited_file = os.path.join(output_dir, 'visited_documents.json')
    visited = {}
    if os.path.exists(visited_file):
        with open(visited_file, 'r', encoding='utf-8') as f:
            visited = json.load(f)
    visited[object_id] = url
    with open(visited_file, 'w', encoding='utf-8') as f:
        json.dump(visited, f, ensure_ascii=False, indent=2)

def get_document_by_id(object_id, version, catalog_name, language):
    if is_document_visited(object_id):
        print(f'Document {object_id} has already been visited.')
        return None

    url = 'https://svc-drcn.developer.huawei.com/community/servlet/consumer/cn/documentPortal/getDocumentById'
    payload = {
        "objectId": object_id,
        "version": version,
        "catalogName": catalog_name,
        "language": language
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        mark_document_as_visited(object_id, url)  # 传递 URL 到标记函数
        return response
    else:
        print(f'请求失败，状态码: {response.status_code}')
        return None
        
# 读取 ui_navigation_results.json 文件
# 修改主逻辑部分
try:
    with open('output/ui_navigation_results.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data:
            doc_name = item.get('url').split('/')[-1]

            response = get_document_by_id(
                doc_name,
                "",
                "harmonyos-references",
                "cn"
            )
            
            if response:
                # 从item中获取URL用于生成文件名
                url = item.get('url', f"document_{doc_name}")
                filename = os.path.join(output_dir, get_filename_from_url(url))
                page = json.loads(response.content).get('value', '').get('content', '').get('content', '')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(page)
                print(f"成功保存 {url} 的内容到 {filename}")
            else:
                print("item 中缺少必要的字段 (objectId, version, catalogName 或 language)")
except requests.RequestException as e:
    print(f"请求 {url} 时出错: {e}")
except FileNotFoundError:
    print("未找到 ui_navigation_results.json 文件")
except json.JSONDecodeError:
    print("解析 ui_navigation_results.json 文件时出错")
