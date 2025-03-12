import random

from ArkTSHelper.codeMutation.layoutConstructors.columnLayout import ColumnLayout
from ArkTSHelper.codeMutation.layoutConstructors.flexLayout import FlexLayout
from ArkTSHelper.codeMutation.layoutConstructors.rowLayout import RowLayout
from ArkTSHelper.codeMutation.layoutConstructors.stackLayout import StackLayout


def generate_example(comp1, comp2):

        # 随机选择布局类型
        layout = random.choice([FlexLayout(), RowLayout(), ColumnLayout(), StackLayout()])

        # 生成布局代码
        layout_code, imports = layout.wrap_children(comp1, comp2)

        # 构建完整代码
        full_code = \
        f"""build() {{
{layout_code}
}}"""

        return full_code




if __name__ == "__main__":
    for i in range(10):
        # 生成示例
        print(f"示例{i}：")
        print(
            generate_example("Button('Submit').type(ButtonType.Capsule)", "Button('Submit').type(ButtonType.Capsule)"))
