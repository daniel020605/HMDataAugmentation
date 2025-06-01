import json

def extract_fields(input_file, output_file, fields_to_extract):
    """
    从指定的 JSON 文件中提取每个元素的某些字段，并存储到一个新的 JSON 文件中。

    :param input_file: 输入 JSON 文件路径
    :param output_file: 输出 JSON 文件路径
    :param fields_to_extract: 要提取的字段列表
    """
    try:
        # 读取输入 JSON 文件
        with open(input_file, 'r', encoding='utf-8') as infile:
            data = json.load(infile)
        
        # 提取每个元素的指定字段
        extracted_data = []
        for item in data:
            extracted_item = {field: item.get(field) for field in fields_to_extract}
            extracted_data.append(extracted_item)
        
        # 将提取的字段写入新的 JSON 文件
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(extracted_data, outfile, ensure_ascii=False, indent=4)
        
        print(f"提取完成，结果已保存到 {output_file}")
    
    except FileNotFoundError:
        print(f"文件 {input_file} 未找到。")
    except json.JSONDecodeError:
        print(f"文件 {input_file} 不是有效的 JSON 文件。")
    except Exception as e:
        print(f"发生错误: {e}")

# 示例用法
if __name__ == "__main__":
    # 输入 JSON 文件路径
    input_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/EG_extracted_pre_tags_with_instructions.json"
    # 输出 JSON 文件路径
    output_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/EG_generate_instruction.json"
    # 要提取的字段列表
    fields_to_extract = ["instruction", "pre"]
    
    # 调用函数
    extract_fields(input_file, output_file, fields_to_extract)

    # 输入 JSON 文件路径
    input_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/EG_extracted_pre_tags_with_instructions.json"
    # 输出 JSON 文件路径
    output_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/EG_code_description.json"
    # 要提取的字段列表
    fields_to_extract = ["description", "pre"]
    
    # 调用函数
    extract_fields(input_file, output_file, fields_to_extract)

     # 输入 JSON 文件路径
    input_file = "/Users/liuxuejin/Desktop/Projects/PythonTools/data/dataset_functions_0505.json"
    # 输出 JSON 文件路径
    output_file = "/Users/liuxuejin/Desktop/Projects/PythonTools/data/IC_generate_instruction.json"
    # 要提取的字段列表
    fields_to_extract = ["query", "variables", "imports", "code"]
    
    # 调用函数
    extract_fields(input_file, output_file, fields_to_extract)

    # 输入 JSON 文件路径
    input_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/FU_dataset_functions_0423.json"
    # 输出 JSON 文件路径
    output_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/CD_code_description_0423.json"
    # 要提取的字段列表
    fields_to_extract = ["variables", "imports", "code", "description"]
    
    # 调用函数
    extract_fields(input_file, output_file, fields_to_extract)

         # 输入 JSON 文件路径
    input_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/FU_dataset_ui_code_0423.json"
    # 输出 JSON 文件路径
    output_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/IC_UI_generate_instruction.json"
    # 要提取的字段列表
    fields_to_extract = ["query", "variables", "imports", "code"]
    
    # 调用函数
    extract_fields(input_file, output_file, fields_to_extract)

    # 输入 JSON 文件路径
    input_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/FU_dataset_ui_code_0423.json"
    # 输出 JSON 文件路径
    output_file = "/Users/liuxuejin/Desktop/Data/生成、解释、补全数据/CD_UI_code_description_0423.json"
    # 要提取的字段列表
    fields_to_extract = ["variables", "imports", "code", "description"]
    
    # 调用函数
    extract_fields(input_file, output_file, fields_to_extract)