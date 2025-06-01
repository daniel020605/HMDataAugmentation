import json
import openai
from openai import OpenAI
from tqdm import tqdm
import os

# Replace with your OpenAI API key
api_key = "sk-72c4ee8b03084b5d9536e70cb61492a6"
base_url = "https://api.deepseek.com"
client = OpenAI(api_key=api_key, base_url=base_url)

def process_object_with_openai(obj):
    # Replace this with your specific prompt logic
    prompt = f'''### 你是谁
    你是一个鸿蒙移动端开发专家，主要使用的开发语言是ArkTS。
    ### 你要做什么
    1. 你需要阅读一段鸿蒙接口介绍，将其整理成流畅的文本，用于为大模型提供知识和生成示例的指导（description）。
    2. 你还需要生成4个用来向大模型提问这条接口描述的指令（instruction）。
    ### 要求
    1. 你不需要生成代码，你只需要提供接口的描述和对应的指令。
    2. 不要在思考时就开始编写，在完全思考后给出你的答案。
    3. 最后以如下Json格式输出：{{
        "instruction": [...],
        "description": "接口描述内容"
    }}
    接口介绍：{obj.get("parent_text")}
    '''

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
        {"role": "system", "content": "You are a helpful assistant, who is good at programming with ArkTS."},
        {"role": "user", "content": prompt},],
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
        "id": obj.get("id"),
        "pre": obj.get("pre"),
        "type": obj.get("type"),
        "function_call": obj.get("function_call"),
        "function_name": obj.get("function_name"),
        "parent_text": obj.get("parent_text"),
        "import_module": obj.get("import_module"),
        "instruction": res.get("instruction"),
        "description": res.get("description"),
        "file_path": obj.get("file_path"),
    }
    return new_obj

def load_existing_data(output_file):
    """Load existing data from the output file."""
    if not os.path.exists(output_file):
        return {}
    with open(output_file, 'r', encoding='utf-8') as file:
        try:
            return {item['id']: item for item in json.load(file)}
        except json.JSONDecodeError:
            return {}

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

def main():
    input_file = "data/extracted_harmonyos-references.json"  
    output_file = "output/extracted_pre_tags_with_instructions.json"
    
    process_json_file(input_file, output_file)
    
    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    main()