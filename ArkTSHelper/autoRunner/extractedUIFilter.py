
from pathlib import Path
import os
import glob


def extract_build(content):
    build_pos = content.find('build()')
    if build_pos == -1:
        return content, "", ""

    # 找到 build() 的起始大括号
    pre_end = build_pos
    while pre_end < len(content) and content[pre_end] != '{':
        pre_end += 1
    if pre_end >= len(content):
        return content[:build_pos], "", content[build_pos:]

    # 匹配 build() 的大括号块
    stack = 1
    build_start = build_pos
    build_end = build_start
    while build_end < len(content) and stack > 0:
        if content[build_end] == '{':
            stack += 1
        elif content[build_end] == '}':
            stack -= 1
        build_end += 1

    return content[:build_start], content[build_start:build_end]


def process_all_subfolders(root_folder):
    """
    将文件夹下每个子文件夹中的ets文件提取出build板块并放入指定模版
    核心流程：
    1. 遍历根目录下的所有子文件夹
    2. 找到每个子文件夹中唯一的 .ets 文件
    3. 创建临时空文件并执行合并操作
    4. 清理临时文件
    """
    # 遍历根目录下的所有子文件夹
    for subdir_name in os.listdir(root_folder):
        subdir_path = os.path.join(root_folder, subdir_name)

        # 跳过非文件夹
        if not os.path.isdir(subdir_path):
            continue

        ets_files = glob.glob(os.path.join(subdir_path, "*.ets"))

        if len(ets_files) != 1:
            print(f"跳过 {subdir_name}: 找到 {len(ets_files)} 个 ets 文件 (需要正好 1 个)")
            continue

        original_path = ets_files[0]


        try:
            content = Path(original_path).read_text(encoding='utf-8')
            before_build, build = extract_build(content)

            new_content = f"""{before_build}
@Entry
@Component
struct Index {{
{build}
}}
""".strip()
            Path(original_path).write_text(new_content)

        except Exception as e:
            print(f"处理失败 {subdir_name}: {str(e)}")


if __name__ == "__main__":
    # 配置根目录路径
    ROOT_FOLDER = "/Users/jiaoyiyang/harmonyProject/repos/extractedUIProjects"  # 修改为你的实际路径

    # 执行处理
    process_all_subfolders(ROOT_FOLDER)
    print("所有子文件夹处理完毕")