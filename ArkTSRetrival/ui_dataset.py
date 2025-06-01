import os
import json
from typing import Dict, List

def read_file_content(file_path: str) -> str:
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def process_folder(folder_path: str) -> Dict[str, str]:
    """处理单个文件夹B的内容"""
    folder_name = os.path.basename(folder_path)
    result = {
        "instruction": "",
        "input": "",
        "output": ""
    }
    
    for file in os.listdir(folder_path):
        result["instruction"] = "你是一个乐于助人的鸿蒙应用开发助手。"
        file_path = os.path.join(folder_path, file)
        if file.endswith('.ets'):
            result["input"] = "请你解释下面的鸿蒙代码：" + read_file_content(file_path)
        elif file.endswith('.txt'):
            result["output"] = read_file_content(file_path)
    
    return result

def main(folder_a_path: str, output_path: str) -> None:
    """主处理函数"""
    dataset = []
    
    for folder_b in os.listdir(folder_a_path):
        folder_b_path = os.path.join(folder_a_path, folder_b)
        if os.path.isdir(folder_b_path):
            data = process_folder(folder_b_path)
            if data["instruction"] and data["input"]:
                dataset.append(data)
    
    # 保存为JSON文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"处理完成，共处理{len(dataset)}条数据，已保存到 {output_path}")

if __name__ == "__main__":
    # 配置路径
    folder_a_path = "/Users/liuxuejin/Downloads/combined_collected"  # 替换为实际的文件夹A路径
    output_path = "/Users/liuxuejin/Desktop/Projects/PythonTools/CD_ui_dataset.json"  # 输出文件路径
    
    # 运行处理
    main(folder_a_path, output_path)