import re
from pathlib import Path
import itertools
from typing import Dict, Set, Tuple
from ArkTSHelper.codeMutation.layoutConstructors.layoutConstructor import generate_example


def merge_ets_files(file1_path: str, file2_path: str, output_path: str):
    """
    合并两个ETS文件的工具函数

    :param file1_path: 第一个ets文件路径
    :param file2_path: 第二个ets文件路径
    :param output_path: 输出文件路径
    """
    # 定义正则表达式模式（增强版）
    import_pattern = re.compile(
        r'import\s+{([\w\s,]+)}\s+from\s+[\'"](.+?)[\'"];',  # 匹配具名导入
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

    def parse_imports(content: str) -> Dict[str, Set[str]]:
        """解析import语句为结构化字典"""
        imports_dict = {}
        for match in import_pattern.finditer(content):
            members = {m.strip() for m in match.group(1).split(',') if m.strip()}
            lib = match.group(2).strip()
            if lib in imports_dict:
                imports_dict[lib].update(members)
            else:
                imports_dict[lib] = members
        return imports_dict

    def generate_imports(imports_dict: Dict[str, Set[str]]) -> str:
        """生成合并后的import语句"""
        output = []
        for lib in sorted(imports_dict.keys()):
            members = sorted(imports_dict[lib])
            output.append(f"import {{ {', '.join(members)} }} from '{lib}';")
        return '\n'.join(output)

    def parse_file(file_path: str) -> Tuple[Dict[str, Set[str]], str, str, str]:
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

    # 解析文件
    imports1, pre1, comp1, post1 = parse_file(file1_path)
    imports2, pre2, comp2, post2 = parse_file(file2_path)

    build_contents, build_imports = build_content_merge(comp1, comp2)
    if imports1.__contains__("@@kit.ArkUI"):
        imports1["@kit.ArkUI"] = imports1["@kit.ArkUI"].union(build_imports)
    else:
        imports1["@kit.ArkUI"] = set(build_imports)

    # 合并imports
    merged_imports = {}
    for lib in set(itertools.chain(imports1.keys(), imports2.keys())):
        merged_imports[lib] = imports1.get(lib, set()) | imports2.get(lib, set())

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
        "/Users/jiaoyiyang/harmonyProject/repos/singleFileProjects/ColorExample/index.ets",
        "/Users/jiaoyiyang/harmonyProject/repos/singleFileProjects/DividerCustomizationExample/DividerCustomizationExample.ets",
        "/Users/jiaoyiyang/harmonyProject/repos/mutationProjects/merged.ets"
    )