from ArkTSHelper.codeMutation.layoutConstructors.baseLayout import BaseLayout, FlexAlign, FlexDirection, FlexWrap, ItemAlign, _weighted_choice
import random
from typing import List

class FlexLayout(BaseLayout):
    def distribute_space(self, children: List[str]) -> List[str]:
        """弹性布局子元素分配策略"""
        # 保持原有分配策略，可与容器参数配合使用
        return children

    def _get_component_name(self):
        params = self._get_layout_params()
        params_str = ", ".join(params) if params else ""
        return f"Flex({{ {params_str} }})"

    def __init__(self):
        super().__init__()
        # 优化方向选择权重（Row/Column占80%）
        self.direction = _weighted_choice(
            options=FlexDirection,
            weights={
                FlexDirection.Row: 0.4,
                FlexDirection.Column: 0.4,
                FlexDirection.RowReverse: 0.1,
                FlexDirection.ColumnReverse: 0.1
            }
        ).value

        # 智能换行策略（根据方向自动调整）
        self.wrap = self._smart_wrap_choice()
        self._cached_params = None

    def _smart_wrap_choice(self):
        """根据方向选择换行策略"""
        if self.direction in [FlexDirection.Column.value, FlexDirection.ColumnReverse.value]:
            return FlexWrap.NoWrap.value  # 纵向布局默认不换行
        return random.choices(
            population=[FlexWrap.NoWrap, FlexWrap.Wrap],
            weights=[0.3, 0.7],  # 横向布局70%概率换行
            k=1
        )[0].value

    def _get_layout_params(self):
        """生成符合设计规范的布局参数"""
        if not self._cached_params:
            base_params = [
                f"direction: {self.direction}",
                f"wrap: {self.wrap}"
            ]

            # 主轴对齐（90%概率设置）
            if random.random() < 0.9:
                main_align = _weighted_choice(
                    options=FlexAlign,
                    weights={
                        FlexAlign.Start: 0.3,
                        FlexAlign.Center: 0.3,
                        FlexAlign.SpaceBetween: 0.25,
                        FlexAlign.SpaceAround: 0.1,
                        FlexAlign.SpaceEvenly: 0.05
                    }
                ).value
                base_params.append(f"justifyContent: {main_align}")

            # 交叉轴对齐（多行布局用alignContent，单行用alignItems）
            if self.wrap != FlexWrap.NoWrap.value:
                cross_align = _weighted_choice(
                    options=FlexAlign,
                    weights={
                        FlexAlign.Start: 0.5,
                        FlexAlign.Center: 0.4,
                        FlexAlign.SpaceBetween: 0.1
                    }
                ).value
                base_params.append(f"alignContent: {cross_align}")
            else:
                if random.random() < 0.7:  # 70%概率设置单行对齐
                    item_align = _weighted_choice(
                        options=ItemAlign,
                        weights={
                            ItemAlign.Start: 0.3,
                            ItemAlign.Center: 0.4,
                            ItemAlign.Stretch: 0.2,
                            ItemAlign.Baseline: 0.1
                        }
                    ).value
                    base_params.append(f"alignItems: {item_align}")

            self._cached_params = base_params
        return self._cached_params

    def _get_method_chain(self):
        """保持方法链扩展性"""
        return []