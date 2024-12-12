from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
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

retriever = vectordb.as_retriever()
llm = ChatOpenAI()

system_prompt = (
    """ 你是一个擅长ArkTS的鸿蒙领域辅助编程代码工具AI助手，你的回答应该是可以运行的代码或逻辑正确的伪代码。对于你不了解的知识，请尝试从context中推理，
你还可以搜索互联网，你可以使用合理的推断，但不要编造答案。
{context}"""
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(llm, prompt)
chain = create_retrieval_chain(retriever, question_answer_chain)

if __name__ == '__main__':
    question = "请你为我解释BackupExtension"
    result = chain.invoke({"input": question})
    print(result["answer"])
