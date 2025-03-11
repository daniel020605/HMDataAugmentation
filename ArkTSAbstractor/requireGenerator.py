import json
import os
from fileinput import filename

import requests

def get_generation(func):
    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": "Qwen/QwQ-32B",
        "stream": False,
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "tools": [],
        "messages": [{"content": f'''假如你是一个鸿蒙移动端开发专家，主要使用的开发语言是ArkTS，现在要求你阅读以下ArkTS代码，理解这段代码的含义，并生成<Question,Solution>数据对，其中Question要求你描述「生成代码的要求」，描述这个要求时，假设你并不知道其对应的代码实现，并比较凝练地描述代码生成的需求，但不需要描述代码细节，即“请你为我生成一个……的代码”，Solution是「原始代码」本身。
待理解代码：「{func}」
你的回答格式**必须**有且只有如下内容：
	{{"question":"生成代码的要求",
	"solution":"原始代码"}}
''',
                      "role": "system"}]
    }
    headers = {
        "Authorization": "Bearer sk-aywqjowbbboyusjqlzfbgnmzkcbqjxkrpeymyzuapwyqobsl",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        print(response.json())
        return response.json()['choices'][0]['message']['content']
    return None

def process_file(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        if file_path.endswith('.json'):
            datas = json.load(file)
            results = []
            for data in datas:
                results.append(get_generation(data[1]))
            if results:
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    json.dump(results, output_file, indent=4, ensure_ascii=False)

def process_folder(folder_path, output_folder):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        output_path = os.path.join(output_folder, file)
        process_file(file_path, output_path)


if __name__ == '__main__':
    # result = get_generation("function listStyle() {\n  .width(CommonConstants.FULL_WIDTH_PERCENT)\n  .borderRadius($r('app.float.radius_16'))\n  .backgroundColor(Color.White)\n  .padding({ left: $r('app.float.scan_tip_margin_top'), right: $r('app.float.scan_tip_margin_top') })\n  .margin({ bottom: $r('app.float.scan_tip_margin_top') })\n}")
    process_file()