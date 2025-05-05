import random
from typing import List, Tuple

from ArkTSHelper.codeMutation.layoutConstructors.columnLayout import ColumnLayout
from ArkTSHelper.codeMutation.layoutConstructors.flexLayout import FlexLayout
from ArkTSHelper.codeMutation.layoutConstructors.rowLayout import RowLayout
from ArkTSHelper.codeMutation.layoutConstructors.stackLayout import StackLayout


def generate_example(comp1, comp2):

        # 随机选择布局类型
        layout = random.choice([FlexLayout(), RowLayout(), ColumnLayout(), StackLayout(), ColumnLayout(), FlexLayout()])

        # 生成布局代码
        layout_code, imports = layout.wrap_children(comp1, comp2)

        # 构建完整代码
        full_code = \
        f"""build() {{
{layout_code}
}}"""

        return full_code , imports

def generate_example_1(children: List[str]) -> Tuple[str, List[str]]:
    """生成包含多个子组件的布局示例"""
    # 随机选择布局类型（与wrap_children_array逻辑匹配）
    layouts = [
        FlexLayout(), RowLayout(), ColumnLayout(),FlexLayout(), StackLayout(),
        StackLayout(), FlexLayout(), ColumnLayout() , ColumnLayout(),ColumnLayout() ,ColumnLayout()
    ]
    layout = random.choice(layouts)

    # 生成布局代码
    layout_code, imports = layout.wrap_children_array(children)

    # 构建完整组件代码
    full_code = \
        f"""
build() {{
{layout_code}
}}"""

    return full_code, imports


if __name__ == "__main__":
    for i in range(1):
        # 生成示例
        print(f"示例{i}：")
        com_list = ["Button('Submit').type(ButtonType.Capsule)", "Button('Submit').type(ButtonType.Capsule)","Button('Submit')"]
        # 创建包含动态子组件的布局
        example_code, required_imports = generate_example_1(com_list)

        # 输出结果
        print("IMPORTS:", required_imports)
        print("CODE:\n", example_code)
