import re
from pathlib import Path
import itertools
from typing import Dict, Set, Tuple
from ArkTSHelper.codeMutation.layoutConstructors.layoutConstructor import generate_example

# 定义正则表达式模式（增强版）
import re
from typing import Dict, Tuple, Set
# 增强版正则表达式（精确匹配三种导入类型）
import_pattern = re.compile(
        r'import\s+'
        r'(?:'
        r'({[\w\s,]+})'  # 情况1：纯命名导入 {A, B}
        r'|'  # 或
        r'((?:\w+)(?:\s*,\s*{[\w\s,]+})?)'  # 情况2：默认导入或混合导入
        r')'
        r'\s+from\s+["\']([^"\']+)["\']\s*;?',
        re.MULTILINE
    )

component_pattern = re.compile(
        r'@Entry\s*'  
        r'@Component\w*\s*'  
        r'(?:export\s+)?'
        r'struct\s+\w+\s*'
        r'\{.*?^\}'
        r'\s*$',
        flags=re.DOTALL | re.MULTILINE | re.VERBOSE
    )


def parse_imports(content: str) -> Dict[str, Tuple[Set[str], Set[str]]]:
    """解析导入语句，返回结构：{lib: (default_imports, named_imports)}"""
    imports_dict = {}

    for match in import_pattern.finditer(content):
        # 正则捕获组解包
        pure_named = match.group(1)  # 纯命名导入捕获组
        default_mixed = match.group(2)  # 默认/混合导入捕获组
        lib = match.group(3).strip()  # 库路径

        # 初始化存储
        default_imports = set()
        named_imports = set()

        # 情况1：处理纯命名导入 {A, B}
        if pure_named:
            named_str = pure_named.strip('{}').strip()
            if named_str:
                named_imports.update(s.strip() for s in named_str.split(','))

        # 情况2：处理默认/混合导入
        elif default_mixed:
            # 分离默认导入和可能的命名部分（例如："a, {B, C}"）
            parts = [p.strip() for p in default_mixed.split(',', 1)]

            # 处理默认导入部分
            if parts[0] and not parts[0].startswith('{'):
                default_imports.add(parts[0])

            # 处理混合的命名导入部分
            if len(parts) > 1 and parts[1].startswith('{'):
                named_str = parts[1].strip('{}').strip()
                if named_str:
                    named_imports.update(s.strip() for s in named_str.split(','))

        # 合并到字典
        if lib:
            existing = imports_dict.get(lib, (set(), set()))
            imports_dict[lib] = (
                existing[0].union(default_imports),
                existing[1].union(named_imports)
            )

    return imports_dict


def generate_imports(imports_dict: Dict[str, Tuple[Set[str], Set[str]]]) -> str:
    """生成合并后的import语句（支持默认/命名导入分离）"""
    output = []
    for lib in sorted(imports_dict.keys()):
        default_members, named_members = imports_dict[lib]

        # 处理默认导入（最多一个有效）
        default_part = ""
        if default_members:
            sorted_default = sorted(default_members)
            if len(sorted_default) > 1:
                print(f"警告: 库 {lib} 存在多个默认导入，仅保留第一个")
            default_part = sorted_default[0]

        # 处理命名导入
        named_part = ""
        if named_members:
            sorted_named = sorted(named_members)
            named_part = "{ " + ", ".join(sorted_named) + " }"

        # 组合语句逻辑
        if default_part and named_part:
            line = f"import {default_part}, {named_part} from '{lib}';"
        elif default_part:
            line = f"import {default_part} from '{lib}';"
        elif named_part:
            line = f"import {named_part} from '{lib}';"
        else:
            continue  # 跳过空导入

        output.append(line)

    return "\n".join(output)


def parse_file(file_path: str) -> tuple[dict[str, tuple[set[str], set[str]]], str, str, str]:
    """解析文件返回结构化数据"""
    content = Path(file_path).read_text(encoding='utf-8')

    # 解析imports
    imports_dict = parse_imports(content)
    # 处理组件内容
    component_match = component_pattern.search(content)
    if not component_match:
        raise ValueError(f"未找到有效组件结构：{file_path}")

    start = component_match.start()
    end = component_match.end()
    pre_content = re.sub(import_pattern, '', content[:start]).strip()  # 移除已解析的import
    component_content = component_match.group(0)
    post_content = content[end:].strip()

    return imports_dict, pre_content, component_content, post_content


def merge_ets_files(file1_path: str, file2_path: str, output_path: str):
    """
    合并两个ETS文件的工具函数

    :param file1_path: 第一个ets文件路径
    :param file2_path: 第二个ets文件路径
    :param output_path: 输出文件路径
    """
    # 解析文件
    imports1, pre1, comp1, post1 = parse_file(file1_path)
    imports2, pre2, comp2, post2 = parse_file(file2_path)

    build_contents, build_imports = build_content_merge(comp1, comp2)
    existing = imports1.get("@kit.ArkUI", (set(), set()))
    imports1["@kit.ArkUI"] = (
        existing[0],
        existing[1].union(build_imports)
    )

    merged_imports = {}
    for lib in set(itertools.chain(imports1.keys(), imports2.keys())):
        # 分别获取两个字典中的默认和具名导入集合（若无则用空集合）
        default1, named1 = imports1.get(lib, (set(), set()))
        default2, named2 = imports2.get(lib, (set(), set()))

        # 合并集合（使用并集操作符 |）
        merged_default = default1 | default2
        merged_named = named1 | named2

        merged_imports[lib] = (merged_default, merged_named)

    # 合并其他内容
    merged_pre = '\n\n'.join(filter(None, [pre1, pre2]))
    merged_post = '\n\n'.join(filter(None, [post1, post2]))


    # 生成最终内容
    final_content = f"""
{generate_imports(merged_imports)}

{merged_pre}

{build_contents}

{merged_post}
""".strip()

    # 写入文件
    Path(output_path).write_text(final_content, encoding='utf-8')


def extract_build_parts(text):
    """
    返回一个三元组 (pre_build, build_content, post_build)
    - pre_build: build() 方法之前的代码
    - build_content: build() 方法体内的代码
    - post_build: build() 方法之后的代码
    """
    # 1. 定位整个 struct 的大括号范围（包含嵌套）
    struct_start = text.find('struct ')
    if struct_start == -1:
        return "", "", ""

    brace_pos = text.find('{', struct_start)
    if brace_pos == -1:
        return "", "", ""

    stack = 1
    content_end = brace_pos + 1
    while content_end < len(text) and stack > 0:
        if text[content_end] == '{':
            stack += 1
        elif text[content_end] == '}':
            stack -= 1
        content_end += 1

    struct_content = text[brace_pos + 1: content_end - 1].strip()

    # 2. 在 struct 内容中分割 build() 方法
    build_pos = struct_content.find('build()')
    if build_pos == -1:
        return struct_content, "", ""

    # 找到 build() 的起始大括号
    pre_end = build_pos
    while pre_end < len(struct_content) and struct_content[pre_end] != '{':
        pre_end += 1
    if pre_end >= len(struct_content):
        return struct_content[:build_pos], "", struct_content[build_pos:]


    # 匹配 build() 的大括号块
    stack = 1
    build_start = pre_end + 1
    build_end = build_start
    while build_end < len(struct_content) and stack > 0:
        if struct_content[build_end] == '{':
            stack += 1
        elif struct_content[build_end] == '}':
            stack -= 1
        build_end += 1

    pre_build = struct_content[:build_pos].strip()
    build_content = struct_content[pre_end+1:build_end-1].strip()
    post_build = struct_content[build_end:].strip()

    return pre_build, build_content, post_build


def build_content_merge(comp1, comp2):
    # 提取build方法内容
    before_build1, build1, after_build1 = extract_build_parts(comp1)
    before_build2, build2, after_build2 = extract_build_parts(comp2)
    merged_build, imports = generate_example(build1, build2)
    res = before_build1+ '\n' +before_build2 + '\n'+ merged_build+ '\n' + after_build1 + '\n'+ after_build2
    return f"""
@Entry
@Component
struct Index {{
{res}
}}
""".strip() , imports


if __name__ == "__main__":
    merge_ets_files(
        "/Users/jiaoyiyang/harmonyProject/repos/singleFileProjects/Youtube-MusicRankList/RankList.ets",
        "/Users/jiaoyiyang/harmonyProject/repos/singleFileProjects/Word-Check_1CalendarPage/CalendarPage.ets",
        "/Users/jiaoyiyang/harmonyProject/repos/merged.ets"
    )