import os
import shutil

import regex  # 需要 pip install regex
import re
import random
dead_root =  '/Users/jiaoyiyang/harmonyProject/repos/combined_dead'
# 预定义的合法资源列表
AI_RESOURCE_WHITELIST = {
    "circle_viewfinder",
    "keyboard",
    "lightbulb_max",
    "panels",
    "pause",
    "phone",
    "phone_doc",
    "play",
    "playing",
    "read_aloud",
    "retouch",
    "screenshot",
    "search",
    "subtitles",
    "translate",
    "translation"
}

import regex

def fix_foreach_parentheses(content: str) -> str:
    """
    补全 ForEach 代码块缺失的闭合括号
    逻辑：定位 => { ... } 结构，检查闭合后是否有 )
    """
    chars = list(content)
    i = 0
    while i < len(chars):
        # 查找 "ForEach" 关键词
        if i + 6 < len(chars) and ''.join(chars[i:i+7]) == 'ForEach':
            state = {
                'found_arrow': False,  # 是否找到 =>
                'brace_stack': 0,      # 大括号嵌套层级
                'insert_pos': -1       # 需要插入括号的位置
            }

            # 遍历后续字符分析结构
            j = i + 7
            while j < len(chars):
                # 查找箭头函数 =>
                if not state['found_arrow']:
                    if chars[j] == '=' and j+1 < len(chars) and chars[j+1] == '>':
                        state['found_arrow'] = True
                        j += 2  # 跳过 =>
                    else:
                        j += 1
                    continue

                # 查找第一个 {
                if state['brace_stack'] == 0:
                    if chars[j] == '{':
                        state['brace_stack'] = 1
                        j += 1
                        continue
                    else:
                        j += 1
                        continue

                # 匹配大括号层级
                if chars[j] == '{':
                    state['brace_stack'] += 1
                elif chars[j] == '}':
                    state['brace_stack'] -= 1

                    # 找到最外层闭合 }
                    if state['brace_stack'] == 0:
                        # 跳过后续空白符
                        k = j + 1
                        while k < len(chars) and chars[k] in (' ', '\t', '\n', '\r'):
                            k += 1

                        # 检查是否缺少闭合 )
                        if k >= len(chars) or chars[k] != ')':
                            state['insert_pos'] = j + 1  # 在 } 后插入 )
                        break
                j += 1

            # 执行插入操作
            if state['insert_pos'] != -1:
                chars.insert(state['insert_pos'], ')')
                i = state['insert_pos']  # 跳过已处理部分
            else:
                i = j
        else:
            i += 1

    return ''.join(chars)


def read_ets_file(file_path: str) -> str:
    """安全读取ETS文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败 {file_path}: {str(e)}")
        raise


def write_ets_file(file_path: str, content: str):
    """安全写回ETS文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"成功更新文件：{file_path}")
    except Exception as e:
        print(f"写入文件失败 {file_path}: {str(e)}")
        raise

def process_content(original: str) -> str:
    modified = original
    modified = re.sub(
        r'^\s*\.alignSelf\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = re.sub(
        r'^\s*\.border\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = re.sub(
        r'^\s*\.wrap\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = re.sub(
        r'^\s*\.selected\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = re.sub(
        r'^\s*\.text\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = re.sub(
        r'^\s*\..*?Wrap\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = re.sub(
        r'^\s*\.justifyContent\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = re.sub(
        r'^\s*\.[a-zA-Z0-9_]+Align\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = re.sub(
        r'^\s*\.alignItems\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = re.sub(
        r'^\s*\.fill([a-zA-Z0-9_]+)?\(.*?\)\s*$',
        '',
        modified,
        flags=re.MULTILINE
    )
    modified = fix_foreach_parentheses(modified)
    modified = re.sub(
        r'(this\.[a-zA-Z0-9_]+\s*\([^()]*\))'  # this.method()
        r'((\s*\n\s*\.[^\n]*)+)',  # 后续的任意数量链式调用
        r'\1',
        modified,
        flags=re.MULTILINE
    )


    def replace_ai_resource(match: re.Match) -> str:
        """替换非白名单资源"""
        resource_name = match.group(1)
        if resource_name in AI_RESOURCE_WHITELIST:
            return match.group(0)
        return f"$r('sys.media.AI_{random.choice(list(AI_RESOURCE_WHITELIST))}')"

    modified = re.sub(
        r"\$r\('sys\.media\.AI_(.*?)'\)",
        replace_ai_resource,
        modified,
        flags=re.IGNORECASE
    )
    return modified

def process_ets_files(root_dir):
    match =[]
    """处理ETS文件并执行自动化流程"""
    count = -1
    for subdir, _, files in os.walk(root_dir):
        if subdir == root_dir:
            continue
        count += 1
        ets_files = [f for f in files if f.endswith('.ets')]
        if len(ets_files) == 1:
            ets_file = ets_files[0]
            file_path = os.path.join(subdir, ets_file)

            # 1. 读取文件内容
            content = read_ets_file(file_path)

            # 2. 处理内容
            modified = process_content(content)

            # 3. 判断是否有实际修改
            if modified == content:
                print(f"无变更跳过：{subdir}")
                match.append(subdir)
                continue

            write_ets_file(file_path, modified)
    print(f"共处理 {count} 个ets文件")

    print("\n找到以下未变更:")
    for i, path in enumerate(match, 1):
        print(f"  {i}. {path}")
    confirm = input("\n确认要这些文件夹到dead吗？(y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    success = 0
    failure = 0
    for folder in match:
        try:

            subdir_name = os.path.basename(folder)
            dead_path = os.path.join(dead_root, subdir_name)
            shutil.move(folder, dead_path)

            print(f"成功移动: {folder}")
            success += 1

        except Exception as e:
            print(f"删除失败 [{type(e).__name__}]: {folder} - {str(e)}")
            failure += 1


if __name__ == '__main__':

    failed_root = "/Users/jiaoyiyang/harmonyProject/repos/combined_failed"
    process_ets_files(failed_root)
