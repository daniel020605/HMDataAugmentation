import json
import re

def parse_import_modules(import_part):
    modules = []
    import_part = import_part.strip()
    
    # 处理包含别名的情况，例如 "A as B"
    def extract_name(part):
        if ' as ' in part:
            return part.split(' as ')[0].strip()
        return part.strip()
    
    if '{' in import_part:
        parts = import_part.split('{', 1)
        default_part = parts[0].strip()
        if default_part:
            for item in re.split(r',\s*', default_part):
                if item:
                    modules.append(extract_name(item))
        named_part = parts[1].split('}', 1)[0]
        for item in re.split(r',\s*', named_part):
            item = item.strip()
            if item:
                modules.append(extract_name(item))
    else:
        for item in re.split(r',\s*', import_part):
            item = item.strip()
            if item:
                modules.append(extract_name(item))
    return modules

def extract_import_features(code):
    import_pattern = re.compile(
        r"import\s+((?:.|\n)+?)\s+from\s+['\"](.*?)['\"]\s*;",
        re.DOTALL
    )
    matches = import_pattern.findall(code)
    features = set()
    for import_part, package in matches:
        package = package.strip()
        modules = parse_import_modules(import_part)
        for module in modules:
            features.add(f"{module}@{package}")
    return features

def load_examples(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        examples = json.load(f)
    for example in examples:
        code = example.get('pre', '')
        example['features'] = extract_import_features(code)
    return examples

def jaccard_similarity(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union != 0 else 0

def find_topk_similar_examples(user_code, examples, topk=3):
    user_features = extract_import_features(user_code)
    similarities = []
    for example in examples:
        example_features = example['features']
        sim = jaccard_similarity(user_features, example_features)
        similarities.append( (example, sim) )
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:topk]

def weighted_merge_results(str_results, chroma_results, str_weight=0.6, chroma_weight=0.4):
    """
    合并两种方法的结果，加权计算最终得分
    str_results: [(example, sim), ...] 来自str_match的结果
    chroma_results: [(example, score), ...] 来自chromadb的结果
    """
    merged = {}
    
    # 处理str_match结果
    for example, sim in str_results:
        merged[example['id']] = {
            'example': example,
            'str_score': sim,
            'chroma_score': 0,
            'total_score': sim * str_weight
        }
    
    # 处理chromadb结果
    for example, score in chroma_results:
        print("--------------------")
        print(example)
        print("--------------------")

        if example['id'] in merged:
            merged[example['id']]['chroma_score'] = score
            merged[example['id']]['total_score'] += score * chroma_weight
        else:
            merged[example['id']] = {
                'example': example,
                'str_score': 0,
                'chroma_score': score,
                'total_score': score * chroma_weight
            }
    
    # 按总分排序
    sorted_results = sorted(merged.values(), key=lambda x: x['total_score'], reverse=True)
    return [(item['example'], item['total_score']) for item in sorted_results]


def mix_search(user_code, examples, topk=5):
    """
    综合使用字符串匹配和向量检索
    返回: [(example, score), ...]
    """
    # 使用字符串匹配方法
    str_results = find_topk_similar_examples(user_code, examples, topk)
    
    # 使用向量检索方法
    from test_chromadb_build import chroma_search
    chroma_results = chroma_search(user_code, topk=topk)
    
    # 合并结果
    final_results = weighted_merge_results(str_results, chroma_results)
    
    return final_results[:topk]

import json
from tqdm import tqdm
from str_match import find_topk_similar_examples, weighted_merge_results
from test_chromadb_build import chroma_search

def process_json_file(input_file, output_file, examples, topk=5):
            """
            遍历 JSON 文件，将字符串匹配和向量检索的结果添加到每个数据项中，并存储到新文件中。
            """
            # 加载输入文件数据
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 遍历每个数据项
            for item in tqdm(data):
                # 检查imports是否为字典列表
                imports = item.get("imports", [])
                if not imports:
                    continue

                # 处理imports为字典的情况
                if isinstance(imports[0], dict):
                    # 提取导入语句，假设字典中有statement字段
                    import_statements = []
                    for imp in imports:
                        # 根据实际字典结构调整字段名
                        if 'statement' in imp:
                            import_statements.append(imp['statement'])
                        elif 'code' in imp:
                            import_statements.append(imp['code'])
                        # 添加更多可能的字段名
                    user_code = "\n".join(import_statements)
                else:
                    # 原始逻辑，处理imports为字符串列表的情况
                    user_code = "\n".join(imports)

                if not user_code:
                    continue

                # 方法1: 使用字符串匹配查找相似示例
                str_results = find_topk_similar_examples(user_code, examples, topk=topk)

                # 方法2: 使用 ChromaDB 查找相似示例
                chroma_results = chroma_search(user_code, topk=topk)

                # 合并两种方法的结果
                final_results = weighted_merge_results(str_results, chroma_results)

                # 将结果添加到当前数据项中
                item["similar_examples"] = [
                    {
                        "id": example["id"],
                        "score": score,
                        "code_snippet": example["pre"],
                        "parent_text": example.get("parent_text", ""),
                    }
                    for example, score in final_results
                    if example.get("type") != "Import"
                ]

            # 将更新后的数据写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

import os

def process_json_folder(input_folder, output_folder, examples, topk=5):
    """
    处理一个文件夹内的所有JSON文件，并将结果存储到另一个文件夹中的同名JSON文件。

    Args:
        input_folder (str): 输入文件夹路径
        output_folder (str): 输出文件夹路径
        examples (list): 示例数据列表，用于匹配
        topk (int): 返回的相似结果数量
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取输入文件夹中的所有JSON文件
    json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    # 处理每个JSON文件
    for json_file in json_files:
        input_file_path = os.path.join(input_folder, json_file)
        output_file_path = os.path.join(output_folder, json_file)

        print(f"处理文件: {json_file}")
        process_json_file(input_file_path, output_file_path, examples, topk=topk)

    print(f"所有文件处理完成，结果已保存到 {output_folder}")

# # 示例使用
# if __name__ == "__main__":
#
#     # 示例数据文件路径
#     input_file = "data/dataset_ui_code_0505.json"  # 输入文件路径
#     output_file = "output/dataset_ui_code_0505.json"  # 输出文件路径
#
#     # 加载示例数据
#     examples = load_examples('data/extracted_harmonyos-references.json')
#
#     # 处理 JSON 文件
#     process_json_file(input_file, output_file, examples, topk=5)
#
#     print(f"处理完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    # 示例文件夹路径
    input_folder = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/projects_abstracted"  # 输入文件夹路径
    output_folder = "output/matchOutput"  # 输出文件夹路径

    # 加载示例数据
    examples = load_examples('data/extracted_harmonyos-references.json')

    # 处理文件夹内的所有JSON文件
    process_json_folder(input_folder, output_folder, examples, topk=5)

    