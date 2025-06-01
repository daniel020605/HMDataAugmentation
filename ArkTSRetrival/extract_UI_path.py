import json

def extract_items_by_path_prefix(json_data, prefix_list):
    """
    从JSON数据中提取出 "path" 字段以给定列表中的字符串为开头的所有条目。

    :param json_data: 包含JSON数据的列表或字典
    :param prefix_list: 用于匹配 "path" 前缀的字符串列表
    :return: 符合条件的条目列表
    """
    result = []
    # 检查输入的JSON数据是否为列表
    if isinstance(json_data, list):
        for item in json_data:
            if "path" in item and isinstance(item["path"], str):
                for prefix in prefix_list:
                    if item["path"].startswith(prefix):
                        result.append(item)
                        break
    return result

def main(json_file_path, prefix_list):
    try:
        # 打开并加载JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        # 提取符合条件的条目
        extracted_items = extract_items_by_path_prefix(json_data, prefix_list)
        return extracted_items
    except FileNotFoundError:
        print(f"指定的JSON文件 {json_file_path} 未找到。")
    except json.JSONDecodeError:
        print(f"无法解析 {json_file_path} 中的JSON数据。")

if __name__ == "__main__":
    # 替换为你的JSON文件路径
    json_file_path = 'data/navigation_results.json'
    # 替换为你想要匹配的前缀列表
    prefix_list = ['应用框架 > ArkUI（方舟UI框架） > ArkTS API ', '应用框架 > ArkUI（方舟UI框架） > ArkTS组件 ']
    result = main(json_file_path, prefix_list)
    with open("output/ui_navigation_results.json", 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)
