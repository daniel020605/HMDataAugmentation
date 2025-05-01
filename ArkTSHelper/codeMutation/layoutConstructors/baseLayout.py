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
        for i in range(random.randint(0, 3)):
            if i == 0:
                generator = create_generator('Top')
            else:
                generator = create_generator()
            extra_components.append(generator.generate())
            imports.extend(generator.imports)

        if len(extra_components) > 0:
            children = (
                    extra_components[:1]
                    + [comp1]
                    + extra_components[1:2]
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

    def wrap_children_array(
            self,
            children: List[str],
            *,
            delete_rate: float = 0.20,  # 删除概率 0-1
            swap_rate: float = 0.35,  # 换位概率
            max_add: int = 3,  # 最大添加数量
            layout_intensity: float = 0.3  # 布局样式强度
    ) -> Tuple[str, List[str]]:
        """包装子元素数组并实现随机操作"""
        imports = []
        extra_components = []

        # 生成基础额外组件
        num_extras = random.randint(0, max_add)
        for i in range(num_extras):
            generator = create_generator('Top' if i == 0 else None)
            comp = generator.generate()
            extra_components.append(comp)
            imports.extend(generator.imports)

        # 合并原始组件和额外组件
        all_components = children + extra_components

        # 随机删除 (保留至少1个元素)
        if len(all_components) > 1:
            all_components = [c for c in all_components
                              if (not c.startswith('this.')
                              and random.random() > delete_rate) or c.startswith('this.')]

        # 随机换位
        if len(all_components) >= 2 and random.random() < swap_rate:
            idx1, idx2 = random.sample(range(len(all_components)), 2)
            all_components[idx1], all_components[idx2] = all_components[idx2], all_components[idx1]

        # 添加动态生成的组件
        new_generator = create_generator()
        for _ in range(random.randint(0, max_add)):
            new_component = new_generator.generate()
            insert_pos = random.randint(0, len(all_components))
            all_components.insert(insert_pos, new_component)
            imports.extend(new_generator.imports)

        # 处理布局样式
        styled_components = []
        for comp in self.distribute_space(all_components):
            if comp.startswith('this.'):
                styled_components.append(comp)
                continue

            # 随机添加组件级样式
            if random.random() < layout_intensity:
                comp = self._add_component_style(comp)
            styled_components.append(comp)

        # 构建布局代码
        layout_code = [f"{self._get_component_name()}{{"]

        # 添加带缩进的子组件
        layout_code.extend(f"  {comp}" for comp in styled_components)
        layout_code.append("}")

        # 添加容器级布局样式
        if not any(c.startswith('this.') for c in all_components):
            layout_code.extend(self._get_layout_styles(layout_intensity))

        return '\n'.join(layout_code), imports

    # 新增辅助方法
    def _add_component_style(self, comp: str) -> str:
        """为单个组件添加样式"""
        styles = []
        if random.random() < 0.2:
            styles.append(f".padding({random.randint(10, 20)})")
        if random.random() < 0.25:
            styles.append(f".width('{random.choice(['100%', '50%', '200px'])}')")
        if random.random() < 0.15:
            styles.append(f".backgroundColor({random_color()})")
        return comp + ''.join(styles)

    def _get_layout_styles(self, intensity: float) -> List[str]:
        """生成容器级布局样式"""
        styles = []
        if random.random() < intensity:
            styles.append(".width('100%')")
        if random.random() < intensity * 0.7:
            styles.append(f".padding({random.randint(5, 20)})")
        return styles


    @abstractmethod
    def _get_component_name(self):
        pass