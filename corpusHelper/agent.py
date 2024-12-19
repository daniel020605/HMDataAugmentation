import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

import configparser

config = configparser.ConfigParser()
config.read("../secret.properties")

os.environ["OPENAI_API_KEY"] = config.get("DEFAULT", "OPENAI_API_KEY")
os.environ["OPENAI_BASE_URL"] = config.get("DEFAULT", "OPENAI_BASE_URL")


embedding = OpenAIEmbeddings()
# 向量数据库保存位置
persist_directory = 'docs/chroma/'
# 从向量数据库加载向量数据库
vectordb = Chroma(persist_directory=persist_directory,
                  embedding_function=embedding)


from langchain.prompts import PromptTemplate

# Build prompt
# template = """Use the following pieces of context to answer the question at the end. \
# If you don't know the answer, just say that you don't know, don't try to make up an answer. \
# Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" \
# at the end of the answer.
# {context}
# Question: {question}
# Helpful Answer:"""

template = """ 你是一个擅长ArkTS的鸿蒙领域辅助编程代码工具AI助手，你的回答应该是可以运行的代码或逻辑正确的伪代码。对于你不了解的知识，请尝试从context中推理，你可以使用合理的推断，但不要编造答案。
{context}
问题: {question}
答案:"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
# 查看向量数据库中的文档数量

from langchain_openai import ChatOpenAI

# 创建llm
llm = ChatOpenAI(temperature=0)

from langchain.chains import RetrievalQA


qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb.as_retriever()
)

# 问题=这门课的主要主题是什么?

# Run chain
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)

# docs = vectordb.similarity_search(question, k=3)
if __name__ == '__main__':
    question = "请你为我解释BackupExtension"

    result = qa_chain.invoke({"query": question})
    print(result["result"])
    print(result["source_documents"])


