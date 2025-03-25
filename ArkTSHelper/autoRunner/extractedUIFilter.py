
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
        content = Path(original_path).read_text(encoding='utf-8')
        positions = find_onclick_positions(content)

        # 从后往前删除避免影响索引
        for start, end in reversed(positions):
            content = content[:start] + content[end:]
        #print(original_path, content)
        Path(original_path).write_text(content, encoding='utf-8')


def find_onclick_positions(content):
    """通过栈匹配闭合的)定位所有onClick事件的起止索引"""
    positions = []
    i = 0
    length = len(content)
    target = '.onClick('

    while i < length:
        # 查找目标字符串.onClick(
        if content[i:i + len(target)] == target:
            start = i
            i += len(target)  # 移动到左括号(之后
            stack = [')']  # 初始化栈，用于追踪闭合括号
            in_string = False
            string_char = None

            # 开始扫描闭合括号
            while i < length:
                char = content[i]

                # 处理字符串中的转义字符
                if not in_string and char in ('"', "'", '`'):
                    in_string = True
                    string_char = char
                elif in_string:
                    if char == string_char and (i == 0 or content[i - 1] != '\\'):
                        in_string = False

                # 仅在非字符串中处理括号
                if not in_string:
                    if char == '(':
                        stack.append(')')
                    elif char == ')':
                        if stack and stack[-1] == ')':
                            stack.pop()
                            if not stack:  # 栈空，找到闭合位置
                                positions.append((start, i + 1))
                                break
                        else:
                            break  # 括号不匹配，提前结束
                i += 1
        else:
            i += 1

    return positions

if __name__ == "__main__":
    # 配置根目录路径
    ROOT_FOLDER = "/Users/jiaoyiyang/harmonyProject/repos/newExtracted"  # 修改为你的实际路径

    # 执行处理
    process_all_subfolders(ROOT_FOLDER)
    print("所有子文件夹处理完毕")