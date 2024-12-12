import json
import requests
from openai import OpenAI


url_generate = "http://localhost:11434/api/generate"
url_chat = "http://localhost:11434/api/chat"



def get_generate_response(url, data):
    response = requests.post(url, json=data)
    response_dict = json.loads(response.text)
    response_content = response_dict["response"]
    return response_content
# data = {
#     "model": "codellama",
#     "prompt": "Why is the sky blue?",
#     "stream": False
# }


def get_code_completion(messages, max_tokens=512, model="codellama"):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        stop=[
            "<step>"
        ],
        frequency_penalty=1,
        presence_penalty=1,
        top_p=0.7,
        n=10,
        temperature=0.7,
    )

    return chat_completion

if __name__ == '__main__':
    client = OpenAI(
        # base_url='http://localhost:11434/v1/',
        # required but ignored
        base_url="https://api.ltss.cc/api/v1/client/subscribe?token=1fcb398a4d5e2820eb84a8d9f5c4b4c4",
        api_key='gpt-3.5-turbo',
    )
    prompt = "你是一位专业程序员，现在要求你处理下面的文档，你的输出格式是一个列表，形如" \
        "[{},{},{}...]，其中每个元素是一个字典，字典中包含三个键值对，分别是'context','question'和'answer'。"\
        "对于有代码的文档，对于每个代码块，要求你将该代码块完整提取出来（注意：你不能修改代码块中的代码）并填充到'answer'字段，"\
        "并结合上下文为相应代码块生成对应的解释，填充到'question'字段，对于'context'字段，请用简要的语言描述该元素的主题或内容。"\
        "对于没有代码的文档，你需要将文档全部的内容转换为若干个问题-答案数据对，分别对应到'question'和'answer'字段，"\
        "对于'context'字段，请用简要的语言描述该元素的主题或内容。请严格按照格式输出。"
    print(prompt)
    with open("../webCrawler/harmonyos-guides-V5/access-dataability-V5.txt", "r") as f:
        messages = [
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": f.read(),
            }
        ]

    chat_completion = get_code_completion(messages)
    print(chat_completion.choices[0].message.content)