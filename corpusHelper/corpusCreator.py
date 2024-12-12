import os
import numpy as np
# pypdf chromadb pip install -U langchain-community

import configparser

config = configparser.ConfigParser()
config.read("../secret.properties")

os.environ["OPENAI_API_KEY"] = config.get("DEFAULT", "OPENAI_API_KEY")
os.environ["OPENAI_BASE_URL"] = config.get("DEFAULT", "OPENAI_BASE_URL")


from langchain_community.document_loaders.json_loader import JSONLoader
from pprint import pprint

# 通过json加载器加载json数据
# file_path = "docs/datas/records.json"
# data = json.loads(Path(file_path).read_text())

# pprint(data)

loader = JSONLoader(
    file_path="docs/datas/records.json",
    jq_schema=".[].[]",
)
data = loader.load()
pprint(data)



docs = []
docs.extend(data)
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=150
)
# 切割文档
splits = text_splitter.split_documents(docs)


from langchain_openai import OpenAIEmbeddings


embedding = OpenAIEmbeddings()


from langchain_community.vectorstores import Chroma

# 向量数据库保存位置
persist_directory = 'docs/chroma/'

# 创建向量数据库
vectordb = Chroma.from_documents(
    documents=splits,
    embedding=embedding,
    persist_directory=persist_directory
)

