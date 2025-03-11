# component_generators.py
import random
from typing import Tuple, List, Dict
from abc import ABC, abstractmethod


class ComponentGenerator(ABC):
    """组件生成器基类"""

    @property
    @abstractmethod
    def imports(self) -> List[str]:
        """需要导入的模块"""
        pass

    @abstractmethod
    def generate(self) -> str:
        """生成组件代码"""
        pass


# --------------------------
# 具体组件生成器实现
# --------------------------
class BlankGenerator(ComponentGenerator):
    @property
    def imports(self):
        return ["Blank"]

    def generate(self):
        styles = [
            f"color({random_color()})"
        ]
        return apply_styles("Blank()", styles)


class TextGenerator(ComponentGenerator):
    @property
    def imports(self):
        return []

    def generate(self):
        content_options = [
            "Section", "Info", "Note",
            "Label", "Description", "Tip"
        ]
        text = random.choice(content_options)

        styles = [
            f"fontColor({random_color()})",
            f"margin({{ {random_margin()} }})",
            f"fontSize({random.randint(12, 32)})",
            f"fontColor({random_color()})",
            f"textAlign(TextAlign.{random.choice(['Start', 'Center', 'End'])})",
            f"decoration({get_decoration()})",
            f"lineHeight({random.choice([1.2, 1.5, 2.0])})",
            f"letterSpacing({random.randint(-2, 5)})",
            f"baselineOffset({random.randint(-20, 30)})",
        ]
        return apply_styles(f"Text('{text}')", styles)


class DividerGenerator(ComponentGenerator):
    @property
    def imports(self):
        return ["Divider"]

    def generate(self):
        styles = [
            f"color({random_color()})",
            f"strokeWidth({random.randint(1, 3)})",
            f"margin({{ {random_margin()} }})"
        ]
        return apply_styles("Divider()", styles)


# --------------------------
# 辅助函数
# --------------------------
def random_color() -> str:
    """生成随机颜色"""
    colors = ["Gray", "Black", "Red", "Blue", "Green"]
    return f"Color.{random.choice(colors)}"

def get_decoration() -> str:
    decorations = [
        f"{{ type: TextDecorationType.LineThrough, color: {random_color()} }}",
        f"{{ type: TextDecorationType.Underline, color: {random_color()} }}",
        f"{{ type: TextDecorationType.Overline, color: {random_color()} }}",
    ]
    return random.choice(decorations)

def random_margin() -> str:
    """生成随机边距"""
    margins = []
    for pos in ["top", "left", "right", "bottom"]:
        if random.random() > 0.5:
            margins.append(f"{pos}: {random.randint(5, 20)}")
    return ", ".join(margins)


def apply_styles(base: str, styles: List[str]) -> str:
    """应用随机样式"""
    if styles and random.random() < 0.8:  # 70%概率添加样式
        selected = random.sample(styles, k=random.randint(0, len(styles) // 2))
        return base + ''.join([f".{s}" for s in selected])
    return base


# --------------------------
# 组件注册表
# --------------------------
GENERATOR_CLASSES = [
    BlankGenerator,
    TextGenerator,
    TextGenerator,
    DividerGenerator,
]


def create_generator() -> ComponentGenerator:
    """创建随机组件生成器"""
    return random.choice(GENERATOR_CLASSES)()



if __name__ == '__main__':
    # 生成10个不同组件
    for _ in range(10):
        code  = create_generator().generate()
        print(f"生成组件：{code}")