import json
import os

import requests
from tqdm import tqdm


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
        "messages": [{"content": f'''### 你是谁
你是一个鸿蒙移动端开发专家，主要使用的开发语言是ArkTS。
### 你要做什么
1. 你需要认真阅读一段「ArkTS代码」，理解代码的内涵，并分析代码中的关键部分。
2. 为代码中的关键部分添加注释。
### 要求
1. 不能修改代码原来的内容。
2. 不要在思考时就添加注释，在完全思考后再为代码添加注释。
3. 你最后的输出要求为
    ```typescript
        添加注释后的代码
    ```
待注释代码：「{func}」
''',
                      "role": "system"}]
    }
    headers = {
        "Authorization": "Bearer sk-oezjkjuambvrdxbcwccqwdiwsxansglgjqooszcioqbwpwns",
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
                        "comment_code" : get_generation(data),
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
    process_file("./test_data.json", "./data/comment/output_data_002.json")
    # process_file("/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/function_with_import_plain_ORIGIN_ONLY/Index.ets.json", "./comment/output_data_index.json")