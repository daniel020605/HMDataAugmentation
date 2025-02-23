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


# 主函数
def main():
    # 设置输入 txt 文件的路径和输出文件夹路径
    input_txt_file = "./example.txt"  # 这里填写你的 examples.txt 文件路径
    output_dir = r"C:\Users\sunguyi\Desktop\repos\singleFileProjects"  # 这里填写你希望保存的目标文件夹路径

    # 加载示例数据
    examples = load_examples_from_txt(input_txt_file)

    # 保存示例代码到指定文件夹
    save_examples(examples, output_dir)


if __name__ == "__main__":
    main()
