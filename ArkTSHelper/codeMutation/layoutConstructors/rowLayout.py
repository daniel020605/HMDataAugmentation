from ArkTSHelper.codeMutation.layoutConstructors.baseLayout import BaseLayout, FlexAlign, VerticalAlign, _weighted_choice
import random
from typing import List

class RowLayout(BaseLayout):
    def distribute_space(self, children: List[str]) -> List[str]:
        """行布局空间分配策略"""
        total = len(children)
        strategy = random.choice(['equal', 'weighted'])

        if strategy == 'equal':
            normal_children = [child for child in children if not child.startswith('this.')]
            this_components = [child for child in children if child.startswith('this.')]

            total = len(normal_children)
            width = f"{(90 // total)}%" if random.random() < 0.9 else f"{(100 // total)}%"
            if total == 0:
                return children  # 没有需要布局的组件时直接返回原始列表

            result = []
            for child in children:
                if child in this_components:
                    result.append(child)  # 保留原始this组件
                else:
                    result.append(f"{child}.width('{width}')")
            return result

        elif strategy == 'weighted':
            # 分离组件类型
            layout_children = [child for child in children if not child.startswith('this.')]
            weights = self._generate_weights(len(layout_children)) if layout_children else []
            result = []
            weight_idx = 0
            for child in children:
                if child.startswith('this.'):
                    result.append(child)
                else:
                    if weight_idx < len(weights):
                        result.append(f"{child}.layoutWeight({weights[weight_idx]})")
                        weight_idx += 1
                    else:
                        result.append(child)
            return result

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