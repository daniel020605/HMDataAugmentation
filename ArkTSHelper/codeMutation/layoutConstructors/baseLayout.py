import random
from enum import Enum
from typing import List, Tuple
from abc import ABC, abstractmethod

from ArkTSHelper.codeMutation.simpleComponentGenerator import create_generator


def _weighted_choice(options: Enum, weights: dict):
    """带权重的枚举选择"""
    population = list(options)
    weight_list = [weights.get(opt, 0) for opt in population]
    return random.choices(population, weight_list, k=1)[0]
# 枚举定义
class FlexAlign(Enum):
    Start = "FlexAlign.Start"
    Center = "FlexAlign.Center"
    End = "FlexAlign.End"
    SpaceBetween = "FlexAlign.SpaceBetween"
    SpaceAround = "FlexAlign.SpaceAround"
    SpaceEvenly = "FlexAlign.SpaceEvenly"


class HorizontalAlign(Enum):
    Start = "HorizontalAlign.Start"
    Center = "HorizontalAlign.Center"
    End = "HorizontalAlign.End"


class VerticalAlign(Enum):
    Top = "VerticalAlign.Top"
    Center = "VerticalAlign.Center"
    Bottom = "VerticalAlign.Bottom"

class FlexDirection(Enum):
    Row = "FlexDirection.Row"
    RowReverse = "FlexDirection.RowReverse"
    Column = "FlexDirection.Column"
    ColumnReverse = "FlexDirection.ColumnReverse"

class FlexWrap(Enum):
    NoWrap = "FlexWrap.NoWrap"
    Wrap = "FlexWrap.Wrap"
    WrapReverse = "FlexWrap.WrapReverse"

class Alignment(Enum):
    # 九种基础对齐方式
    TopStart = "Alignment.TopStart"
    Top = "Alignment.Top"
    TopEnd = "Alignment.TopEnd"
    Start = "Alignment.Start"
    Center = "Alignment.Center"
    End = "Alignment.End"
    BottomStart = "Alignment.BottomStart"
    Bottom = "Alignment.Bottom"
    BottomEnd = "Alignment.BottomEnd"

class ItemAlign(Enum):
    Auto = "ItemAlign.Auto"
    Start = "ItemAlign.Start"
    Center = "ItemAlign.Center"
    End = "ItemAlign.End"
    Stretch = "ItemAlign.Stretch"
    Baseline = "ItemAlign.Baseline"

class LayoutType(Enum):
    Row = "Row"
    Column = "Column"
    Flex = "Flex"
    Stack = "Stack"


def random_color() -> str:
    """生成随机颜色"""
    colors = ["Gray", "Black", "Red", "Blue", "Green"]
    return f"Color.{random.choice(colors)}"



class BaseLayout(ABC):
    """线性布局基类"""

    def __init__(self):
        self.adaptive_type = None



    @abstractmethod
    def _get_layout_params(self) -> List[str]:
        """获取布局参数（由子类实现）"""
        pass

    @abstractmethod
    def _get_method_chain(self) -> List[str]:
        """获取方法链调用（由子类实现）"""
        pass

    @abstractmethod
    def distribute_space(self, children: List[str]) -> List[str]:
        pass

    def wrap_children(self, comp1: str, comp2: str) -> Tuple[str, List[str]]:
        """包装子元素通用逻辑"""
        imports = []
        children = []

        # 生成额外组件（0-3个）
        extra_components = []
        imports = []
        for _ in range(random.randint(0, 3)):
            generator = create_generator()
            extra_components.append(generator.generate())
            imports.extend(generator.imports)

        if len(extra_components) > 0:
            # 确保主组件被分隔的插入策略
            children = (
                    extra_components[1:2]
                    + [comp1]
                    + extra_components[:1]
                    + [comp2]
                    + extra_components[2:]
            )
        else:
            children = [comp1, comp2]

        children = self.distribute_space(children)

        # 构建布局代码
        layout_code = [
            f"{self._get_component_name()}{{",
            *[f"  {child}" for child in children],
            "}"
        ]

        # 添加方法链
        layout_code.extend(self._get_method_chain())

        # 添加容器样式
        if random.random() < 0.7:
            layout_code.append(".width('100%')")
        if random.random() < 0.5:
            layout_code.append(".padding(10)")
        if random.random() < 0.20:
            layout_code.append(f".backgroundColor({random_color()})")
        return '\n'.join(layout_code), imports

    @abstractmethod
    def _get_component_name(self):
        pass

