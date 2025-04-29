import json
import openai
from openai import OpenAI
from tqdm import tqdm
import os

# Replace with your OpenAI API key
api_key = "sk-f2435cc41ede4e5cb59f37056979e232"
base_url = "https://api.deepseek.com"
client = OpenAI(api_key=api_key, base_url=base_url)


# Global variable to track the current ID
current_id = 0

def get_next_id():
    """Get the next auto-incrementing ID."""
    global current_id
    current_id += 1
    return current_id


def process_object_with_openai(content):
    # Replace this with your specific prompt logic
    prompt = f'''### 你是谁
    你是一个鸿蒙移动端开发专家，主要使用的开发语言是ArkTS。
    ### 你要做什么
    1. 你需要阅读一段鸿蒙UI代码，理解其逻辑，完成一段对代码的描述，以“这段代码”做开头（description）。
    2. 你还需要生成4个用来向大模型提问这条代码描述的指令（instruction）。
    3. 你需要基于你生成的描述，生成对应的安卓UI代码（使用XML）。
    ### 要求
    1. 不要在思考时就开始编写，在完全思考后给出你的答案。
    2. 最后以如下Json格式输出：{{
        "instruction": [...],
        "description": "接口描述内容",
        "android_code": "安卓UI代码"
    }}
    UI代码：{content}
    '''

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个乐于助人的助手，擅长使用ArkTS编程。"},
            {"role": "user", "content": prompt}, ],
        response_format={
            "type": "json_object",
        },
        stream=False
    )
    try:
        res = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print("Error decoding JSON response:", response.choices[0].message.content)
        return None
    new_obj = {
        "id": get_next_id(),
        "instruction": res.get("instruction", []),
        "description": res.get("description", ""),
        "android_code": res.get("android_code", ""),
        "harmony_code": content
    }
    return new_obj



def load_existing_data(output_file):
    """
    从目标文件中加载现有数据
    :param output_file: 输出文件路径
    :return: 现有数据的字典
    """
    if not os.path.exists(output_file):
        return {}
    with open(output_file, 'r', encoding='utf-8') as f:
        try:
            return {item['file_name']: item for item in json.load(f)}
        except json.JSONDecodeError:
            return {}

def save_data(output_file, data):
    """
    将数据保存到目标文件
    :param output_file: 输出文件路径
    :param data: 要保存的数据
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(list(data.values()), f, ensure_ascii=False, indent=4)


def process_json_file(input_file, output_file):
    # Load existing data from the output file
    existing_data = load_existing_data(output_file)

    # Ensure the output file exists
    if not os.path.exists(output_file):
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump([], file)

    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if isinstance(data, list):
        for obj in tqdm(data):
            if obj.get("type") == 'Import':
                continue
            if obj.get("id") in existing_data:
                print(f"Skipping already processed object with ID {obj.get('id')}")
                continue  # Skip if the object is already processed

            # Process the object
            new_obj = process_object_with_openai(obj)
            if not new_obj:
                print(f"Failed to process object with ID {obj.get('id')}")
                continue

            # Append the new object to the output file
            with open(output_file, 'r+', encoding='utf-8') as file:
                try:
                    current_data = json.load(file)
                except json.JSONDecodeError:
                    current_data = []
                current_data.append(new_obj)
                file.seek(0)
                json.dump(current_data, file, ensure_ascii=False, indent=4)
                file.truncate()
    else:
        raise ValueError("JSON root must be an array.")

import os
import json

def process_ets_content(content):
    """
    处理 .ets 文件内容的逻辑
    :param content: 原始文件内容
    :return: 处理后的数据
    """
    # 示例处理逻辑：将内容转换为大写
    return process_object_with_openai(content)


def process_ets_files(input_folder, output_file):
    """
    遍历文件夹中的 .ets 文件，处理内容并动态存储到指定文件
    :param input_folder: 输入文件夹路径
    :param output_file: 输出文件路径
    """
    # 加载现有数据
    existing_data = load_existing_data(output_file)

    for root, _, files in os.walk(input_folder):
        for file in tqdm(files):
            if file.endswith('.ets'):
                if file in existing_data:
                    print(f"文件 {file} 已处理，跳过。")
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        processed_data = process_ets_content(content)

                        # 更新或添加数据
                        existing_data[file] = {
                            "file_name": file,
                            "processed_data": processed_data
                        }

                        # 动态保存数据
                        save_data(output_file, existing_data)
                        print(f"文件 {file} 已处理并保存。")
                except Exception as e:
                    print(f"读取文件 {file_path} 时发生错误: {e}")


if __name__ == "__main__":
    input_folder = "/Users/liuxuejin/Desktop/Data/etsFiles"  # 输入文件夹路径
    output_file = "./processed_UI_data.json"  # 输出文件路径

    process_ets_files(input_folder, output_file)