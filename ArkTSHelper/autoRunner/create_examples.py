import os
import json
import shutil
from pathlib import Path


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
    1. 为每个 JSON 文件中的每个元素创建一个独立的文件夹
    2. 在每个文件夹中生成一个 .ets 文件
    3. 保留原始文件结构不修改
    """
    # 确保目标根目录存在
    os.makedirs(dst_folder, exist_ok=True)

    root_path = Path(src_folder)
    # 遍历所有子文件夹
    for subdir in root_path.rglob('*'):
        if not subdir.is_dir():
            continue
            # 遍历子文件夹中的文件

        for file in subdir.iterdir():
            filename = file.name
            if not file.is_file():
                continue
            if not filename.endswith(".json"):
                continue

            try:
                # 读取源文件内容
                src_path = os.path.join(src_folder,subdir, filename)
                with open(src_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)


                #print(json_data)
                result = {
                    "full_imports": [item["full_import"] for item in json_data["imports"]],
                    "functions": json_data["functions"],
                    "full_variables": [var["full_variable"] for var in json_data["variables"]],
                    "ui_codes": json_data["ui_code"]
                }

                if not result["ui_codes"]:
                    continue
                base_name =  filename.replace(".json", "").replace(".ets", "")





                dst_subfolder = os.path.join(dst_folder, f"{base_name}")
                # 为每个元素创建一个独立的文件夹
                counter = 0
                target_subdir = dst_subfolder
                # 检查同名子文件夹是否存在
                while os.path.exists(target_subdir):
                    counter += 1
                    target_subdir = f"{dst_subfolder}_{counter}"
                os.makedirs(target_subdir, exist_ok=True)

                # 分步构建内容列表
                content_lines = []

                # 1. 添加 imports
                content_lines.extend(result["full_imports"])

                # 2. 添加组件定义
                content_lines.append("@Entry")
                content_lines.append("@Component")
                content_lines.append("struct Index {")

                # 3. 添加变量（自动缩进）
                for var_line in result["full_variables"]:
                    content_lines.append(f"  {var_line}")

                # 4. 添加函数（自动缩进 + 空行分隔）
                if result["functions"]:
                    content_lines.append("")  # 空行
                    for func in result["functions"]:
                        # 函数体自动缩进
                        func_lines = func.split("\n")
                        content_lines.extend([f"  {line}" for line in func_lines])
                        content_lines.append("")  # 函数后空行

                # 5. 添加 UI 代码（自动缩进）
                if result["ui_codes"]:
                    for ui_line in result["ui_codes"]:
                        # 假设 UI 代码已包含缩进，直接添加
                        content_lines.append(f"    {ui_line}")
                # 6. 闭合结构体
                content_lines.append("}")

                # 合并为最终字符串（自动处理换行）
                content = "\n".join(content_lines).strip()

                # 生成 .ets 文件
                dst_path = os.path.join(target_subdir, f"{base_name}.ets")
                print(dst_path)
                with open(dst_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"成功转换：{filename} → {os.path.relpath(dst_path, dst_folder)}")

            except Exception as e:
                print(f"处理失败 {filename}: {str(e)}")


import os
import shutil


def organize_ets_files(source_dir: str, target_dir: str) -> None:
    """
    将源文件夹中的 .ets 文件移动到目标文件夹的同名子文件夹
    自动处理同名冲突，通过添加序号生成唯一子文件夹
    :param source_dir: 源文件夹路径 (如 "./source")
    :param target_dir: 目标文件夹路径 (如 "./target")
    """
    # 遍历所有 .ets 文件（包含子目录）
    for root, _, files in os.walk(source_dir):
        for filename in [f for f in files if f.endswith(".ets")]:
            source_path = os.path.join(root, filename)
            file_basename = os.path.splitext(filename)[0]  # 无扩展名的文件名

            # 生成唯一子文件夹路径
            base_subdir = os.path.join(target_dir, file_basename)
            target_subdir = base_subdir
            counter = 0

            # 检查同名子文件夹是否存在
            while os.path.exists(target_subdir):
                counter += 1
                target_subdir = f"{base_subdir}_{counter}"

            # 创建子文件夹并移动文件
            os.makedirs(target_subdir, exist_ok=True)
            target_path = os.path.join(target_subdir, filename)
            shutil.move(source_path, target_path)
            print(f"Moved: {source_path} → {target_path}")


# 使用示例
organize_ets_files("/Users/jiaoyiyang/Downloads/鸿蒙UI截图（ets文件＋截图）01", "/Users/jiaoyiyang/harmonyProject/repos/curcollected")

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
    source_folder = r"/Users/jiaoyiyang/harmonyProject/repos/out"  # 原始文件夹
    target_folder = r"/Users/jiaoyiyang/harmonyProject/repos/newExtracted"  # 新生成的目标文件夹

    convert_ets_json_to_new_folder(source_folder, target_folder)

    # # 使用示例
    # organize_ets_files("/Users/jiaoyiyang/Downloads/鸿蒙UI截图（ets文件+截图）02",
    #                    "/Users/jiaoyiyang/harmonyProject/repos/curcollected")


if __name__ == "__main__":
    main()
