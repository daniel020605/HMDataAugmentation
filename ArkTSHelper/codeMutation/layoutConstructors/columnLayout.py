from ArkTSHelper.codeMutation.layoutConstructors.baseLayout import BaseLayout, FlexAlign, HorizontalAlign, _weighted_choice
import random
from typing import List

class ColumnLayout(BaseLayout):
    def distribute_space(self, children: List[str]) -> List[str]:
        """列布局空间分配策略（垂直方向）"""
        total = len(children)
        strategy = random.choice(['equal', 'weighted'])

        if strategy == 'equal':
            # 90%概率使用留白高度，10%概率撑满
            height = f"{(90 // total)}%" if random.random() < 0.9 else f"{(100 // total)}%"
            return [f"{child}.height('{height}')" for child in children]

        elif strategy == 'weighted':
            # 保持权重分配逻辑，主元素占更大比例
            weights = self._generate_weights(total)
            return [f"{child}.layoutWeight({w})" for child, w in zip(children, weights)]

        else:
            return children

    def _generate_weights(self, total: int) -> List[int]:
        """生成权重分布"""
        base = [1] * total
        base[total // 2 - 1] += random.choice([1, 2])
        return base

    def _split_heights(self, total: int) -> List[int]:
        """分配合理的高度百分比"""
        base = [30, 20, 15]  # 常见分配模式
        if total <= 3:
            return base[:total]
        # 对于更多元素采用平均分配
        avg = 80 // total
        return [avg] * (total - 1) + [80 - avg * (total - 1)]

    def _apply_free_style(self, child: str) -> str:
        """自由模式应用样式"""
        if random.random() < 0.6:
            return f"{child}.height('{random.choice([20, 25, 30])}%')"
        return f"{child}.maxHeight(200)"

    def _get_component_name(self):
        params = self._get_layout_params()
        params_str = ", ".join(params) if params else ""
        return f"Column({{ {params_str} }})"

    def _get_layout_params(self):
        params = []
        if random.random() < 0.7:
            params.append(f"space: {random.choice([8, 12, 16])}")
        return params

    def _get_method_chain(self):
        methods = []
        if random.random() < 0.9:
            main_align =  _weighted_choice(
                options=FlexAlign,
                weights={
                    FlexAlign.Start: 0.3,
                    FlexAlign.Center: 0.3,
                    FlexAlign.SpaceBetween: 0.25,
                    FlexAlign.SpaceAround: 0.1,
                    FlexAlign.SpaceEvenly: 0.05,
                    FlexAlign.End: 0.0
                }
            ).value
            methods.append(f".justifyContent({main_align})")
        if random.random() < 0.6:
            methods.append(f".alignItems({random.choice(list(HorizontalAlign)).value})")
        return methods