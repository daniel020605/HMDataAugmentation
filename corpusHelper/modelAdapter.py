import os

import configparser

from bs4 import BeautifulSoup
from sympy import content

config = configparser.ConfigParser()
config.read("../secret.properties")

os.environ["OPENAI_API_KEY"] = config.get("DEFAULT", "OPENAI_API_KEY")
os.environ["OPENAI_BASE_URL"] = config.get("DEFAULT", "OPENAI_BASE_URL")

from langchain.prompts import PromptTemplate

template = """ CREATE TABLE HMFunctions (
    FunctionID SERIAL PRIMARY KEY,
    FunctionName VARCHAR(100),
    FunctionParameters TEXT,
    ReturnType VARCHAR(100),
    ReturnValue TEXT,
    FullFunctionName VARCHAR(255),
    RequiredPermissions VARCHAR(255),
    SystemCapability VARCHAR(255),
    ErrorCodes TEXT,
    Example TEXT,
    FunctionDescription TEXT
);

CREATE TABLE HMClasses (
    ClassID SERIAL PRIMARY KEY,
    ClassName VARCHAR(100),
    MemberVariables TEXT,
    Methods TEXT,
    Constructors TEXT,
    InnerClasses TEXT,
    Example TEXT,
    ClassDescription TEXT
);

CREATE TABLE HMEnums (
    EnumID SERIAL PRIMARY KEY,
    EnumName VARCHAR(100),
    SystemCapability VARCHAR(255),
    EnumValueName VARCHAR(100),
    EnumValue VARCHAR(100),
    Description TEXT
);

CREATE TABLE HMTypeDefinitions (
    TypeID SERIAL PRIMARY KEY,
    TypeName VARCHAR(100),
    TypeCategory VARCHAR(50),
    Description TEXT
);
请你根据上面这些SQL，提取所给文本的相应信息，注意，你的输出应该仅包含若干条SQL语句，你不能修改文本的内容，只能拆分或提炼：
文本: {question}
输出:"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
# 查看向量数据库中的文档数量

from langchain_openai import ChatOpenAI

# 创建llm
llm = ChatOpenAI(temperature=0)


def html_to_text(file_path):
    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the text content
    text_content = soup.get_text()
    print(text_content)
    return text_content

def llm_analyzer(path):
    content = html_to_text(path)
    ctx = QA_CHAIN_PROMPT.invoke({"question": content}).to_string()
    messages = [
        (
            "system",
            "You are a helpful tool for text processing.",
        ),
        ("human", ctx),
    ]
    result = llm.invoke(messages)
    return result.content

if __name__ == '__main__':
    path = "./test.html"
    result = llm_analyzer(path)
    with open("output.sql", "w") as f:
        f.write(result)




