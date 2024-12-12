from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = "sk-Y5El1ncQxjD6o3MM84Ea9572F68d4a2e85341d2847225807"
os.environ["OPENAI_BASE_URL"] = "https://api.xiaoai.plus/v1"


llm = ChatOpenAI()

system_prompt = (
    """你是一位专业程序员，现在要求你处理下面的文档，你的输出格式是一个列表，形如[{{}},{{}},{{}}...]，其中每个元素是一个字典，字典中包含三个键值对，分别是'context',
    'question'和'answer'。对于有代码的文档，对于每个代码块，要求你将该代码块完整提取出来（注意：你不能修改代码块中的代码）并填充到'answer
    '字段，并结合上下文为相应代码块生成对应的解释，填充到'question'字段，对于'context
    '字段，请用简要的语言描述该元素的主题或内容。对于没有代码的文档，你需要将文档全部的内容转换为若干个问题-答案数据对，分别对应到'question'和'answer'字段，对于'context
    '字段，请用简要的语言描述该元素的主题或内容。请严格按照格式输出。 """
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)
chain = prompt|llm


if __name__ == '__main__':
    with open("../webCrawler/harmonyos-guides-V5/access-dataability-V5.txt", "r") as f:
        text = f.read()
    result = chain.invoke({"input": text})
    print(result.content)
