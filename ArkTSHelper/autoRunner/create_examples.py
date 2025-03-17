import os
import json


# 从 txt 文件读取 JSON 格式的 examples 内容
def load_examples_from_txt(txt_file_path):
    with open(txt_file_path, "r", encoding="utf-8") as file:
        examples = json.load(file)
    return examples


def save_examples(examples, output_dir):
    for example_name, example_code in examples.items():
        # 创建文件夹路径
        example_folder = os.path.join(output_dir, example_name)

        # 如果文件夹已存在，从 _1 开始添加后缀
        counter = 1
        original_example_folder = example_folder
        while os.path.exists(example_folder):
            example_folder = f"{original_example_folder}_{counter}"
            counter += 1

        # 创建对应的文件夹
        os.makedirs(example_folder, exist_ok=True)

        # 写入示例代码到对应的 .ets 文件
        example_file_path = os.path.join(example_folder, f"{example_name}.ets")
        with open(example_file_path, "w", encoding="utf-8") as f:
            f.write(example_code)

        print(f"示例 {example_name} 已保存到文件夹 {example_folder}，路径：{example_file_path}")


def convert_ets_json_to_new_folder(src_folder, dst_folder):
    """
    核心逻辑：
    1. 在目标文件夹创建同名子文件夹
    2. 提取 JSON 数组第一个元素
    3. 生成同名 .ets 文件到目标子文件夹
    4. 保留原始文件结构不修改
    """
    # 确保目标根目录存在
    os.makedirs(dst_folder, exist_ok=True)

    # 遍历源文件夹
    for filename in os.listdir(src_folder):
        if not filename.endswith(".ets.json"):
            continue

        # 提取基础名称（去扩展名）
        base_name = filename[:-9]  # 等价于去掉 .ets.json

        try:
            # 读取源文件内容
            src_path = os.path.join(src_folder, filename)
            with open(src_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            # 验证并提取内容
            if not isinstance(json_data, list) or len(json_data) < 1:
                raise ValueError("内容不是有效数组或数组为空")
            content = str(json_data[0])

            # 创建目标子文件夹
            dst_subfolder = os.path.join(dst_folder, base_name)
            os.makedirs(dst_subfolder, exist_ok=True)

            # 写入 .ets 文件
            dst_path = os.path.join(dst_subfolder, f"{base_name}.ets")
            with open(dst_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"成功转换：{filename} → {os.path.relpath(dst_path, dst_folder)}")

        except Exception as e:
            print(f"处理失败 {filename}: {str(e)}")




# 主函数
def main():
    # 设置输入 txt 文件的路径和输出文件夹路径
    # input_txt_file = "./example.txt"  # 这里填写你的 examples.txt 文件路径
    # output_dir = r"/Users/jiaoyiyang/harmonyProject/repos/extractedUIProjects"  # 这里填写你希望保存的目标文件夹路径
    #
    # # 加载示例数据
    # examples = load_examples_from_txt(input_txt_file)
    #
    # # 保存示例代码到指定文件夹
    # save_examples(examples, output_dir)
    # 配置路径（按需修改）
    source_folder = r"/Users/jiaoyiyang/Downloads/processed_ui_with_import_added_import"  # 原始文件夹
    target_folder = r"/Users/jiaoyiyang/harmonyProject/repos/extractedUIProjects"  # 新生成的目标文件夹

    convert_ets_json_to_new_folder(source_folder, target_folder)


if __name__ == "__main__":
    main()
