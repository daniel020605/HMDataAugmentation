import json
import os

import requests
from tqdm import tqdm
from config import configer

url, token = configer.get_llm_config()

def judge(func):
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
        "messages": [{"content": f'''# 代码评价Prompt

### 你是谁

你是一个鸿蒙移动端开发专家，主要使用的开发语言是ArkTS。

### 你要做什么

1. 你要准备用于微调鸿蒙领域知识大模型的数据，现在你需要对一些代码内容进行评估（注意，你不需要对代码正确性进行判断），判断某段代码内容是否符合日常开发需求，是否适合用于进行大模型微调。

### 要求

1. 你的回答只可以是<YES>或<NO>，<YES>表示这段代码适合用于微调， <NO>表示这段代码不适合进行微调。
2. 不要在思考时就做出决定，在完全思考后给出你的答案。
''',
                      "role": "system"},
                     {
                        "content": f"待评价代码：{func}",
                        "role": "user"
                     }]
    }
    headers = {
        "Authorization": "Bearer "+ token,
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        print(response.json())
        return response.json()['choices'][0]['message']['content']
    return None

def process_file(file_path, output_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            if file_path.endswith('.json'):
                datas = json.load(file)
                results = []
                for data in tqdm(datas):
                    results.append({
                        "comment_code" : judge(data),
                        "origin_code" : data
                    })
                if results:
                    with open(output_path, 'w', encoding='utf-8') as output_file:
                        json.dump(results, output_file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

def process_folder(folder_path, output_folder):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        output_path = os.path.join(output_folder, file)
        process_file(file_path, output_path)


if __name__ == '__main__':
    # result = get_generation("function listStyle() {\n  .width(CommonConstants.FULL_WIDTH_PERCENT)\n  .borderRadius($r('app.float.radius_16'))\n  .backgroundColor(Color.White)\n  .padding({ left: $r('app.float.scan_tip_margin_top'), right: $r('app.float.scan_tip_margin_top') })\n  .margin({ bottom: $r('app.float.scan_tip_margin_top') })\n}")
    # process_file("./test_data.json", "./data/comment/output_data_002.json")
    # process_file("/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/function_with_import_plain_ORIGIN_ONLY/Index.ets.json", "./comment/output_data_index.json")

    data = judge("function listStyle() {\n  .width(CommonConstants.FULL_WIDTH_PERCENT)\n  .borderRadius($r('app.float.radius_16'))\n  .backgroundColor(Color.White)\n  .padding({ left: $r('app.float.scan_tip_margin_top'), right: $r('app.float.scan_tip_margin_top') })\n  .margin({ bottom: $r('app.float.scan_tip_margin_top') })\n}")
    print(data)