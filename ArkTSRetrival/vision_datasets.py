import os
import json
import pyarrow as pa
import pyarrow.parquet as pq
from openai import OpenAI
from typing import List, Dict, Any
from tqdm import tqdm
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# 配置OpenAI客户端
api_keys = [
    "sk-72c4ee8b03084b5d9536e70cb61492a6",
    # "sk-9af18059f9d548cea65ca2d5fa0fb28a",
]
base_url = "https://api.deepseek.com"
clients = [OpenAI(api_key=key, base_url=base_url) for key in api_keys]

# 添加全局变量和锁
current_key_index = 0
key_lock = threading.Lock()

def get_client():
    """轮询获取客户端"""
    global current_key_index
    with key_lock:
        client = clients[current_key_index]
        current_key_index = (current_key_index + 1) % len(clients)
    return client

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_android_xml(description: str) -> str:
    try:
        client = get_client()  # 获取当前客户端
        prompt = f"""
        ### 你是谁

        你是一个资深的Android开发专家。

        ### 你要做什么

        1. 你需要阅读一份UI布局介绍文本，并根据文本内容写出对应的XML布局文件，要求该XML文件可以直接通过Android Studio渲染出来。

        ### 要求与注意事项

        1. 对于所有的“android:src”资源引用，都使用相似的安卓自带资源替换，如在ImageView中使用android:src="@android:drawable/ic_menu_search"属性。
        2. 对于tint属性，使用“app:tint"代替“android:tint”。
        3. `layout_toEndOf` 等定位属性只能用于 `RelativeLayout` 的子视图。
        4. 在引用id时要保证有对应id组件被定义，如果没有需要定义，如 android:id="@+id/description"  

        UI布局介绍文本：
        {description}
        """
        
        # Add delay to prevent rate limiting
        time.sleep(1)  # 1 second delay between requests
        
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "你是一个专业的移动端应用开发工程师，擅长开发Android应用和HarmonyOS应用"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            # response_format={
            #     "type": "json_object",
            # },
            stream=False
        )
        
        # Parse response
        try:
            res = response.choices[0].message.content
            # 提取文本中的xml代码块
            if "```xml" in res:
                # 处理带xml标记的代码块
                code_block = res.split("```xml")[1].split("```")[0].strip()
            elif "```" in res:
                # 处理普通代码块
                code_block = res.split("```")[1].split("```")[0].strip()
            else:
                # 处理无代码块标记的响应
                code_block = res.strip()
            return code_block
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Full response: {res}")
            return ""
            
    except Exception as e:
        print(f"Error generating XML: {e}")
        if "400" in str(e) or "rate limit" in str(e).lower():
            print("Waiting 60 seconds due to rate limit...")
            time.sleep(60)
        raise  # Re-raise to trigger retry

def save_to_parquet(data: List[Dict[str, Any]], output_path: str):
    """将数据保存为Parquet文件"""
    # 定义schema
    schema = pa.schema([
        ("folder_name", pa.string()),
        ("png_content", pa.string()),
        ("jpg_content", pa.string()),
        ("ets_content", pa.string()),
        ("txt_content", pa.string()),
        ("generated_xml", pa.string())
    ])
    
    # 创建PyArrow表
    table = pa.Table.from_pylist(data, schema=schema)
    
    # 写入Parquet文件
    pq.write_table(table, output_path)
    print(f"数据已保存到 {output_path}")

def read_file_content(file_path: str) -> str:
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def process_folder(folder_path: str) -> Dict[str, Any]:
    """处理单个文件夹B的内容"""
    folder_name = os.path.basename(folder_path)
    print(f"正在处理文件夹: {folder_name}")
    
    # 检查是否已存在XML文件
    xml_file = os.path.join(folder_path, f"{folder_name}.xml")
    if os.path.exists(xml_file):
        print(f"跳过已处理文件夹(已有XML文件): {folder_name}")
        return None

    record = {
        "folder_name": folder_name,
        "png_content": None,
        "jpg_content": None,
        "ets_content": None,
        "txt_content": None,
        "generated_xml": None
    }
    
    for root, dirs, files in os.walk(folder_path):
        if root != folder_path:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.png'):
                record["png_content"] = file_path
            elif file.endswith('.jpg'):
                record["jpg_content"] = file_path
            elif file.endswith('.ets'):
                record["ets_content"] = read_file_content(file_path)
            elif file.endswith('.txt'):
                record["txt_content"] = read_file_content(file_path)
    
    if record["ets_content"] and record["txt_content"]:
        record["generated_xml"] = generate_android_xml(record["txt_content"])
    
    # 生成XML后保存到文件夹
    if record["generated_xml"]:
        try:
            with open(xml_file, 'w', encoding='utf-8') as f:
                f.write(record["generated_xml"])
            print(f"已保存XML到: {xml_file}")
        except Exception as e:
            print(f"保存XML文件失败: {e}")
    
    return record

def worker(folder_b, folder_a_path):
    """工作线程函数"""
    folder_b_path = os.path.join(folder_a_path, folder_b)
    if os.path.isdir(folder_b_path):
        try:
            record = process_folder(folder_b_path)
            if record:  # 只有当record不为None时才处理
                # 这里需要添加保存记录的代码
                # save_to_parquet([record], output_path)
                pass
        except Exception as e:
            print(f"处理 {folder_b_path} 出错: {e}")

def main(folder_a_path: str) -> None:
    """主处理函数(多线程版本)"""
    folders = [f for f in os.listdir(folder_a_path) if os.path.isdir(os.path.join(folder_a_path, f))]
    
    # 使用线程池处理
    with ThreadPoolExecutor(max_workers=len(api_keys)) as executor:
        futures = []
        for folder_b in folders:
            futures.append(executor.submit(worker, folder_b, folder_a_path))
        
        # 显示进度条
        for future in tqdm(futures, total=len(folders), desc="处理进度"):
            future.result()  # 等待任务完成
    
    print("处理完成")

if __name__ == "__main__":
    # 配置路径
    folder_a_path = "/Users/liuxuejin/Downloads/combined_collected"  # 替换为实际的文件夹A路径
    
    # 运行处理
    main(folder_a_path)