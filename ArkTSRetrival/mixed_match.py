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
from mixed_match import find_topk_similar_examples, weighted_merge_results
from test_chromadb_build import chroma_search


def process_json_file(input_file, output_file, examples, topk=5):
    """处理ProjectAbstractor生成的JSON文件，为每个函数和UI组件添加相似示例"""
    # 加载输入文件数据
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 遍历每个文件项
    for file_item in tqdm(data):
        # 处理函数
        for function in file_item.get("functions", []):
            # 从函数依赖中提取imports
            import_statements = []
            imports = function.get("dependencies", {}).get("imports", [])
            if not imports:
                # 尝试从顶层imports查找对应关系
                file_imports = file_item.get("imports", [])
                for imp in file_imports:
                    if "_ref_path" in imp and imp["_ref_path"].startswith("root") and "dependencies.imports" in imp[
                        "_ref_path"]:
                        imports.append(imp)

            for imp in imports:
                if "name" in imp and imp["name"] and "module_name" in imp:
                    name = imp["name"]
                    module = imp["module_name"]
                    import_type = imp.get("import_type", "named")

                    # 构造import语句
                    if import_type == "default":
                        import_statements.append(f"import {name} from '{module}';")
                    elif import_type == "named":
                        import_statements.append(f"import {{ {name} }} from '{module}';")
                    elif import_type == "namespace":
                        import_statements.append(f"import * as {name} from '{module}';")

            # 获取函数内容
            content = function.get("content", "")

            # 进行检索
            str_results = []
            if import_statements:
                import_code = "\n".join(import_statements)
                str_results = find_topk_similar_examples(import_code, examples, topk=topk)

            chroma_results = []
            if content:
                # 限制content长度，避免token超限
                if len(content) > 10000:  # 保守限制在约6K tokens左右
                    content = content[:10000]
                    print(f"截断过长内容，原长度：{len(function.get('content', ''))}")

                try:
                    chroma_results = chroma_search(content, topk=topk)
                except Exception as e:
                    print(f"向量检索错误: {str(e)}")
                    chroma_results = []

            final_results = weighted_merge_results(str_results, chroma_results)

            # 保存结果
            function["similar_examples"] = [
                {
                    "id": example["id"],
                    "score": score,
                    "code_snippet": example["pre"],
                    "parent_text": example.get("parent_text", "")
                }
                for example, score in final_results
                if example.get("type", "") != "Import"
            ]

        # 处理UI代码 - 与函数处理类似
        for ui_code in file_item.get("ui_code", []):
            import_statements = []
            imports = ui_code.get("dependencies", {}).get("imports", [])

            if not imports:
                # 尝试从顶层imports查找对应关系
                file_imports = file_item.get("imports", [])
                for imp in file_imports:
                    if "_ref_path" in imp and imp["_ref_path"].startswith("root") and "dependencies.imports" in imp[
                        "_ref_path"]:
                        imports.append(imp)

            for imp in imports:
                if "name" in imp and imp["name"] and "module_name" in imp:
                    name = imp["name"]
                    module = imp["module_name"]
                    import_type = imp.get("import_type", "named")

                    if import_type == "default":
                        import_statements.append(f"import {name} from '{module}';")
                    elif import_type == "named":
                        import_statements.append(f"import {{ {name} }} from '{module}';")
                    elif import_type == "namespace":
                        import_statements.append(f"import * as {name} from '{module}';")

            content = ui_code.get("content", "")

            str_results = []
            if import_statements:
                import_code = "\n".join(import_statements)
                str_results = find_topk_similar_examples(import_code, examples, topk=topk)

            chroma_results = []
            if content:
                # 限制content长度，避免token超限
                if len(content) > 10000:
                    content = content[:10000]
                    print(f"截断过长内容，原长度：{len(ui_code.get('content', ''))}")

                try:
                    chroma_results = chroma_search(content, topk=topk)
                except Exception as e:
                    print(f"向量检索错误: {str(e)}")
                    chroma_results = []

            final_results = weighted_merge_results(str_results, chroma_results)

            ui_code["similar_examples"] = [
                {
                    "id": example["id"],
                    "score": score,
                    "code_snippet": example["pre"],
                    "parent_text": example.get("parent_text", "")
                }
                for example, score in final_results
                if example.get("type", "") != "Import"
            ]

    # 将更新后的数据写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

import os


def process_json_folder(input_folder, output_folder, examples, topk=5, force_reprocess=False):
    """
    处理一个文件夹内的所有JSON文件，并将结果存储到另一个文件夹中的同名JSON文件。
    如果输出文件已存在，默认跳过处理，除非指定force_reprocess=True。

    Args:
        input_folder (str): 输入文件夹路径
        output_folder (str): 输出文件夹路径
        examples (list): 示例数据列表，用于匹配
        topk (int): 返回的相似结果数量
        force_reprocess (bool): 是否强制重新处理所有文件，即使输出已存在
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取输入文件夹中的所有JSON文件
    json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    # 处理每个JSON文件
    skipped_count = 0
    processed_count = 0

    for json_file in json_files:
        input_file_path = os.path.join(input_folder, json_file)
        output_file_path = os.path.join(output_folder, json_file)

        # 检查输出文件是否已存在
        if os.path.exists(output_file_path) and not force_reprocess:
            print(f"跳过已处理文件: {json_file}")
            skipped_count += 1
            continue

        print(f"处理文件: {json_file}")
        process_json_file(input_file_path, output_file_path, examples, topk=topk)
        processed_count += 1

    print(f"所有文件处理完成，共处理 {processed_count} 个文件，跳过 {skipped_count} 个文件")
    print(f"结果已保存到 {output_folder}")


if __name__ == "__main__":
    # 示例文件夹路径
    input_folder = "/Volumes/P800/HMImport"
    output_folder = "/Users/liuxuejin/Desktop/Data/HMNewMatch"

    # 加载示例数据
    examples = load_examples('data/extracted_harmonyos-references.json')

    # 处理文件夹内的所有JSON文件，默认跳过已处理文件
    process_json_folder(input_folder, output_folder, examples, topk=5, force_reprocess=False)

    