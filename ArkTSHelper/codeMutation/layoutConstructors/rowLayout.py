from ArkTSHelper.codeMutation.layoutConstructors.baseLayout import BaseLayout, FlexAlign, VerticalAlign, _weighted_choice
import random
from typing import List

class RowLayout(BaseLayout):
    def distribute_space(self, children: List[str]) -> List[str]:
        """行布局空间分配策略"""
        total = len(children)
        strategy = random.choice(['equal', 'weighted'])

        if strategy == 'equal':
            width = f"{(90 // total)}%" if random.random() < 0.9 else f"{(100 // total)}%"
            return [f"{child}.width('{width}')" for child in children]

        elif strategy == 'weighted':
            # 权重分配（主元素权重更高）
            weights = self._generate_weights(total)
            return [f"{child}.layoutWeight({w})" for child, w in zip(children, weights)]

        else:
            return children

    def _generate_weights(self, total: int) -> List[int]:
        """生成权重分布"""
        base = [1] * total
        base[total // 2 - 1] += random.choice([1, 2])
        return base


    def _get_component_name(self):
        params = self._get_layout_params()
        params_str = ", ".join(params) if params else ""
        return f"Row({{ {params_str} }})"

    def _get_layout_params(self):
        params = []
        if random.random() < 0.7:
            params.append(f"space: {random.choice([8, 12, 16])}")
        return params

    def _get_method_chain(self):
        methods = []
        if random.random() < 0.9:
            main_align = _weighted_choice(
                options=FlexAlign,
                weights={
                    FlexAlign.Start: 0.3,
                    FlexAlign.Center: 0.3,
                    FlexAlign.SpaceBetween: 0.25,
                    FlexAlign.SpaceAround: 0.1,
                    FlexAlign.SpaceEvenly: 0.05,
                    FlexAlign.End: 0.0  # 实际开发中End使用较少
                }
            ).value
            methods.append(f".justifyContent({main_align})")
        if random.random() < 0.6:
            methods.append(f".alignItems({random.choice(list(VerticalAlign)).value})")
        return methods