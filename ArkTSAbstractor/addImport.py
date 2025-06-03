import json
import os
import glob
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_project_data(data):
    # 检查数据格式
    if not isinstance(data, list):
        logger.warning("数据格式不是列表，无法处理")
        return data

    # 创建文件路径索引
    file_index = {}
    for item in data:
        if "file" in item:
            file_index[item["file"]] = item

    # 遍历所有数据处理imports
    for item in data:
        # 处理functions
        for func in item.get("functions", []):
            if "dependencies" in func and "imports" in func["dependencies"]:
                process_imports(func["dependencies"]["imports"], file_index)

        # 处理ui_code
        for ui in item.get("ui_code", []):
            if "dependencies" in ui and "imports" in ui["dependencies"]:
                process_imports(ui["dependencies"]["imports"], file_index)

        # 处理classes
        for cls in item.get("classes", []):
            if "dependencies" in cls and "imports" in cls["dependencies"]:
                process_imports(cls["dependencies"]["imports"], file_index)

        # 处理variables
        for var in item.get("variables", []):
            if "dependencies" in var and "imports" in var["dependencies"]:
                process_imports(var["dependencies"]["imports"], file_index)

    return data


def process_imports(imports, file_index):
    for imp in imports:
        # 检查module_name是否以'.'开头
        if "module_name" in imp and imp["module_name"].startswith('.'):
            # 获取resolved_file
            if "resolved_file" in imp:
                resolved_file = imp["resolved_file"]
                # 在文件索引中查找对应的数据
                if resolved_file in file_index:
                    target_item = file_index[resolved_file]
                    # 获取导入的名称
                    import_name = imp.get("name")
                    if import_name:
                        # 在目标文件的各种列表中查找匹配项
                        content_found = False

                        # 检查ui_code
                        for ui in target_item.get("ui_code", []):
                            if ui.get("name") == import_name:
                                imp["xl_content"] = ui.get("content", "")
                                content_found = True
                                break

                        # 如果没找到，检查functions
                        if not content_found:
                            for func in target_item.get("functions", []):
                                if func.get("name") == import_name:
                                    imp["xl_content"] = func.get("content", "")
                                    content_found = True
                                    break

                        # 如果没找到，检查classes
                        if not content_found:
                            for cls in target_item.get("classes", []):
                                if cls.get("name") == import_name:
                                    imp["xl_content"] = cls.get("content", "")
                                    content_found = True
                                    break

                        # 如果没找到，检查variables
                        if not content_found:
                            for var in target_item.get("variables", []):
                                if var.get("name") == import_name:
                                    imp["xl_content"] = var.get("full_variable", "")
                                    break


def process_folder(input_folder, output_folder):
    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 获取所有JSON文件
    json_files = glob.glob(os.path.join(input_folder, "*.json"))

    processed_count = 0
    error_count = 0

    for json_file in json_files:
        try:
            # 读取JSON文件
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"处理 {json_file} 出错: JSON解析错误 - {str(e)}")
                    error_count += 1
                    continue

            # 处理数据
            processed_data = process_project_data(data)

            # 获取输出文件路径
            file_name = os.path.basename(json_file)
            output_file = os.path.join(output_folder, file_name)

            # 保存处理后的数据
            with open(output_file, 'w', encoding='utf-8') as out_f:
                json.dump(processed_data, out_f, ensure_ascii=False, indent=2)

            logger.info(f"已处理: {json_file} -> {output_file}")
            processed_count += 1

        except Exception as e:
            logger.error(f"处理 {json_file} 出错: {str(e)}")
            error_count += 1

    logger.info(f"处理完成。成功: {processed_count} 个文件，失败: {error_count} 个文件")


# 使用示例
if __name__ == "__main__":
    input_folder = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/projects_abstracted"
    output_folder = "/Users/liuxuejin/Desktop/Projects/HMDataAugmentation/ArkTSAbstractor/projects_import"
    process_folder(input_folder, output_folder)