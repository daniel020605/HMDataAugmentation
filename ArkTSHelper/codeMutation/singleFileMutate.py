from typing import List, Optional

from ArkTSHelper.codeMutation.layoutConstructors.layoutConstructor import generate_example_1
from ArkTSHelper.codeMutation.mergeCurrentFile import parse_imports, component_pattern, parse_file, extract_build_parts, \
    generate_imports


def process_single_ets_file(file_path: str)-> str:
    """
    处理单个ets文件变异的函数

    :param file_path: 第一个ets文件路径

    """
    # 解析文件
    imports, pre, comp, post = parse_file(file_path)

    build_contents, build_imports = build_content_mutate(comp)
    existing = imports.get("@kit.ArkUI", (set(), set()))
    imports["@kit.ArkUI"] = (
        existing[0],
        existing[1].union(build_imports)
    )

    # 生成最终内容
    final_content = f"""
{generate_imports(imports)}
{pre}
{build_contents}
{post}
    """.strip()

    return final_content

def build_content_mutate(comp):
    before_build, build_content, after_build = extract_build_parts(comp)
    extractedComps = extract_build_content(build_content)
    mutated_build, imports = generate_example_1(extractedComps)
    res = before_build + mutated_build+ '\n' + after_build
    new_cont = f"""
@Entry
@Component
struct Index {{
{res}
}}
""".strip()
    return  new_cont, imports


def extract_build_content(build_content: str) -> List[str]:
    """
    提取最外层组件的第一层子组件
    """
    components = []
    i = 0
    n = len(build_content)

    # 先去除最外层组件包裹
    outer_removed = remove_outer_wrapper(build_content)

    content = outer_removed


    i = 0
    n = len(content)

    # 主解析循环
    while i < n:
        # 跳过空白和注释
        i = skip_whitespace_and_comments(content, i)
        if i >= n:
            break

        # 检查组件起始位置
        if (content[i].isalpha() or
                (content[i:i + 5] == "this." and i + 5 < n and content[i + 5].isalpha())):

            # 开始解析组件
            component_start = i
            depth = 0
            in_chain = False
            while i < n and content[i]!= '(':
                i += 1

            while i < n:
                # 处理括号嵌套
                if content[i] == '(':
                    depth += 1
                elif content[i] == ')':
                    depth -= 1
                i += 1
                if depth == 0:
                    break

            i = skip_whitespace_and_comments(content, i)
            if content[i] == '{':
                while i < n:
                    if content[i] == '}':
                        depth -= 1
                    if content[i] == '{':
                        depth += 1
                    i += 1
                    if depth ==  0:
                        break

            i = skip_whitespace_and_comments(content, i)
            if content[i] == '.':
                in_chain = True
            while in_chain:
                while i < n:
                    if content[i] == '\n':
                        i += 1
                        break
                    i += 1
                i = skip_whitespace_and_comments(content, i)
                in_chain = (i < n and content[i] == '.')


            # 提取组件内容
            component = content[component_start:i].strip()
            if component:
                components.append(component)
        else:
            i += 1

    return components

def remove_outer_wrapper(s: str) -> str:
    """
    去除最外层组件包裹，返回（内部内容，外层链式调用）

    示例输入：
    Column() {
      content
    }.width(...).height(...)

    返回：
    "content"
    """
    i = 0
    n = len(s)

    # 1. 跳过组件名
    while i < n and s[i] != '(':
        i += 1
    if i >= n:
        return ""

    # 2. 匹配参数括号
    i = find_matching_paren(s, i)
    if i is None:
        return ""

    # 3. 检查是否有大括号
    i = skip_whitespace_and_comments(s, i + 1)
    has_brace = False
    if i < n and s[i] == '{':
        has_brace = True
        i = find_matching_brace(s, i)
        if i is None:
            return ""
        i += 1

    # 4. 提取链式调用
    chain_start = i
    while i < n and (s[i] in ('.', '\n', ' ', '\t') or s[i:i + 2] == '//'):
        if s[i] == '.':
            # 完整匹配链式调用
            while i < n and s[i] not in ('\n', '{', '('):
                i += 1
        else:
            i += 1
    chained = s[chain_start:i].strip()

    # 计算内容范围
    content_start = s.find('{') + 1 if has_brace else s.find(')') + 1
    content_end = s.rfind('}') if has_brace else i
    content = s[content_start:content_end].strip()

    return content


def find_matching_paren(s: str, start: int) -> Optional[int]:
    """找到与起始位置匹配的右括号"""
    depth = 1
    i = start + 1
    while i < len(s):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i
        elif s[i] in ('"', "'"):
            # 跳过字符串
            quote = s[i]
            i += 1
            while i < len(s) and s[i] != quote:
                if s[i] == '\\':
                    i += 1
                i += 1
        i += 1
    return None


def find_matching_brace(s: str, start: int) -> Optional[int]:
    """找到与起始位置匹配的右花括号"""
    depth = 1
    i = start + 1
    while i < len(s):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        elif s[i] in ('"', "'"):
            # 跳过字符串
            quote = s[i]
            i += 1
            while i < len(s) and s[i] != quote:
                if s[i] == '\\':
                    i += 1
                i += 1
        i += 1
    return None


def skip_whitespace_and_comments(s: str, start: int) -> int:
    """跳过空白和注释"""
    i = start
    n = len(s)
    while i < n:
        # 跳过空白
        while i < n and s[i].isspace():
            i += 1

        # 处理行注释
        if i + 1 < n and s[i:i + 2] == '//':
            i += 2
            while i < n and s[i] != '\n':
                i += 1

        # 处理块注释
        elif i + 1 < n and s[i:i + 2] == '/*':
            i += 2
            while i + 1 < n and s[i:i + 2] != '*/':
                i += 1
            i += 2
        else:
            break

    return i

if __name__ == '__main__':
    filePath = "/Users/jiaoyiyang/harmonyProject/repos/mutate_test/0/0.ets"
    print(process_single_ets_file(filePath))