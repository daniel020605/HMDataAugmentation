import os
import time
import requests
from bs4 import BeautifulSoup
import csv
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin
import logging
from HTMLParser import html_to_text
from NJUBoxClient import NJUBoxClient
import configparser

config = configparser.ConfigParser()
config.read("../secret.properties")


urllib3.disable_warnings(InsecureRequestWarning)
MAX_DEPTH = 3
LOCAL_STORAGE = False
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
error_log_file = 'error_log.txt'
csv_file = 'crawled_files.csv'
BASE_URL = 'https://developer.android.com/reference'

# 开关变量和特定字符串
FILTER_ENABLED = True
FILTER_STRING = 'https://developer.android.com/reference'

NJU_ID = config.get("DEFAULT", "NJU_ID")
NJU_PASSWORD = config.get("DEFAULT", "NJU_PASSWORD")
NJU_WEBAPP_NAME = config.get("DEFAULT", "NJU_WEBAPP_NAME")
NJU_REPO_ID = config.get("DEFAULT", "NJU_REPO_ID")
njuClient = NJUBoxClient(NJU_ID, NJU_PASSWORD, NJU_WEBAPP_NAME)



def fetch_url_content(url):
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=3)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = session.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.text
    except Exception as e:
        with open(error_log_file, 'a') as f:
            f.write(f"Error fetching {url}: {e}\n")
        return None

def parse_android_docs(content, base_url):
    soup = BeautifulSoup(content, 'html.parser')
    docs = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('http') or href.startswith('https'):
            full_url = href
        elif href.startswith('//'):
            full_url = f"https:{href}"
        elif href.startswith('/'):
            full_url = urljoin(base_url, href)
        else:
            continue

        if FILTER_ENABLED and not full_url.startswith(FILTER_STRING):
            continue

        docs.append(full_url)
    return docs

def save_docs(docs, output_dir, base_url, depth):
    if depth > MAX_DEPTH:
        return

    os.makedirs(output_dir, exist_ok=True)
    with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        for doc in docs:
            doc_name = doc.replace(BASE_URL, '').replace('/', '_').strip('_') or 'index.html'
            file_path = os.path.join(output_dir, doc_name)

            if not is_url_crawled(doc):
                logging.info(f"Fetching URL: {doc}")
                doc_content = fetch_url_content(doc)
                doc_content = html_to_text(doc_content)
                if doc_content is None:
                    continue

                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(doc_content)

                    if not LOCAL_STORAGE:
                        try:
                            njuClient.uploadFile(file_path, NJU_REPO_ID, '/', 'Android开发文档')
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except Exception as e:
                            with open(error_log_file, 'a') as f:
                                f.write(f"Error uploading {file_path} to NJUBox: {e}\n")


                    csvwriter.writerow([doc, file_path, depth])
                    csvfile.flush()  # 确保数据及时写入文件
                    logging.info(f"Saved document: {doc_name}")
                except Exception as e:
                    with open(error_log_file, 'a') as f:
                        f.write(f"Error saving {doc}: {e}\n")
                time.sleep(2)
                new_docs = parse_android_docs(doc_content, base_url)
                save_docs(new_docs, output_dir, base_url, depth + 1)

def is_url_crawled(url):
    if not os.path.exists(csv_file):
        # 如果没有则创建
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['url', 'file', 'depth'])
        return False
    with open(csv_file, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if row[0] == url:
                return True
    return False

def main():

    content = fetch_url_content(BASE_URL)
    if content is None:
        return
    docs = parse_android_docs(content, BASE_URL)
    save_docs(docs, './android_docs/', BASE_URL, 1)

if __name__ == "__main__":
    main()