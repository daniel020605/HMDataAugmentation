import os
import json
from simhash import Simhash, SimhashIndex

def load_json_files(folder_path):
    """加载指定文件夹下的所有json文件"""
    strings = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 假设每个json文件的内容是一个字符串列表
                    strings.extend(data)
    return strings

def get_features(content):
    """简化特征提取过程"""
    return content.split()

def remove_similar_strings(strings, threshold=3):
    """使用SimHash去除相似的字符串"""
    index = SimhashIndex([], k=threshold)
    unique_strings = []

    for s in strings:
        simhash = Simhash(get_features(s))
        dups = index.get_near_dups(simhash)
        if not dups:
            # 如果没有找到相似项，则添加到唯一字符串列表和索引中
            index.add(len(unique_strings), simhash)
            unique_strings.append(s)
    
    return unique_strings

if __name__ == '__main__':
    folder_path = '/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/complete_function'  # 替换为你的文件夹路径
    strings = load_json_files(folder_path)
    unique_strings = remove_similar_strings(strings)

    print(f"Original number of strings: {len(strings)}")
    print(f"Number of unique strings after deduplication: {len(unique_strings)}")

    # 输出或保存去重后的结果
    for us in unique_strings:
        print(us)