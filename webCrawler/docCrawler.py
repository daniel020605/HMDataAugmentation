import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

VISITED_DOCS_FILE = './dir/visited_docs.txt'


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
        mark_document_as_visited(object_id)
        return response
    else:
        print(f'请求失败，状态码: {response.status_code}')
        return None


def get_content(response):
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # 查找并提取所有<p>和<pre>标签内容
        elements = soup.find_all(['p', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul'])
        non_empty_elements = []

        for element in elements:
            if element.get_text().strip() and not element.find_parents(['p', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul']):
                non_empty_elements.append(element)
                print(element.get_text())

        return non_empty_elements
    else:
        print(f'请求失败，状态码: {response.status_code}')
        return None


def get_catalog(catalog_name):
    url = 'https://svc-drcn.developer.huawei.com/community/servlet/consumer/cn/documentPortal/getCatalogTree'
    payload = {
        "language": "cn",
        "catalogName": catalog_name
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        res = response.json()['value']
        return res.get('catalogTreeList', [])
    else:
        print(f'请求失败，状态码: {response.status_code}')
        return None


def find_leaf_nodes(tree_list):
    tree_leaf_nodes = []

    def traverse(node):
        if node.get('isLeaf'):
            tree_leaf_nodes.append(node.get('relateDocument'))
        else:
            for child in node.get('children', []):
                traverse(child)

    for node in tree_list:
        traverse(node)

    return tree_leaf_nodes


def is_document_visited(object_id):
    try:
        with open(VISITED_DOCS_FILE, 'r') as file:
            visited_docs = file.read().splitlines()
            return object_id in visited_docs
    except FileNotFoundError:
        return False


def mark_document_as_visited(object_id):
    with open(VISITED_DOCS_FILE, 'a') as file:
        file.write(object_id + '\n')


def doc_pipe(doc_name):
    document = get_document_by_id(doc_name, "", "harmonyos-guides-V5", "cn")
    if document:
        doc_paragraphs = get_content(document)
        # print(document.json())
        with open(f'./docs/{doc_name}.txt', 'w') as file:
            for paragraph in doc_paragraphs:
                file.write(paragraph.get_text() + '\n')


if __name__ == '__main__':
    doc_pipe("start-with-ets-stage-V5")
    catalog_tree_list = get_catalog("harmonyos-guides-V5")
    if catalog_tree_list:
        leaf_nodes = find_leaf_nodes(catalog_tree_list)
        # 将leaf_nodes数据存储到本地
        with open('./dir/leaf_nodes.txt', 'w') as file:
            for node in leaf_nodes:
                file.write(node + '\n')

    # 读取leaf_nodes.txt的数据，并逐个请求文档内容
    with open('./dir/leaf_nodes.txt', 'r') as file:
        for line in tqdm(file):
            doc_pipe(line.strip())

    # 计算/docs目录下的文件包括多少字符：9402554

    # 计算/docs目录下的文件包括多少词：1025659


