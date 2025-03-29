import json
import os
import requests
import time
from tool import process_out_json_file
from tqdm import tqdm
from config import configer

url, token = configer.get_llm_config()

def get_generation(func, retries=3, wait=5):
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
1. 你需要阅读一段「ArkTS代码」，理解这段代码的含义，详细分析这段代码的意图和需求点。
2. 在理解代码后生成描述「生成代码的指令」，描述这个要求时，假设你并不知道其对应的代码实现，并比较凝练地描述代码生成的需求，但不需要描述代码细节，即“请你为我生成一个……的代码”，Solution是「原始代码」本身。
### 要求
1. 不要在思考时就写指令，仅在思考后完成你的指令。
2. 你的回答格式**必须** **有且只有** 生成代码的指令。
待理解代码：「{func}」
''',
                      "role": "system"}]
    }
    headers = {
        "Authorization": "Bearer "+token,
        "Content-Type": "application/json"
    }

    for attempt in range(retries):
        try:
            response = requests.request("POST", url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except requests.exceptions.SSLError as e:
            print(f"SSLError encountered: {e}. Retrying in {wait} seconds...")
            time.sleep(wait)
    return None

def process_file(file_path, mode="both"):
    if os.path.isdir(file_path):
        print(f"Skipping directory: {file_path}")
        return [], []

    uis, funcs = process_out_json_file(file_path)
    if uis is None or funcs is None:
        print(f"Error processing file {file_path}")
        return [], []

    ui_res = []
    func_res = []

    for data in tqdm(uis):
        ui_res.append({
            "query": get_generation(data['content']),
            "imports": data["imports"],
            "variables": data["variables"],
            "solution": data["content"]
        })

    for data in tqdm(funcs):
        func_res.append({
            "query": get_generation(data['content']),
            "imports": data["imports"],
            "variables": data["variables"],
            "solution": data["content"]
        })

    return ui_res, func_res

def process_folder(folder_path, output_folder):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        output_path = os.path.join(output_folder, file)

        if os.path.exists(output_path):
            print(f"File {output_path} already exists, skipping...")
            continue
        ui_res, func_res = process_file(file_path)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        print(f"Saving results to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "ui_code": ui_res,
                "functions": func_res
            }, f, indent=2, ensure_ascii=False)

def process_root(root_path, out_path):
    for folder in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder)
        if os.path.isdir(folder_path):
            base_path = os.path.basename(folder_path)
            out_sub_path = os.path.join(out_path, base_path)
            process_folder(folder_path, out_sub_path)

if __name__ == '__main__':
    process_root("./out", "./output_data")