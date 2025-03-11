from ArkTSHelper.codeMutation.layoutConstructors.baseLayout import BaseLayout, Alignment, _weighted_choice
import random
from typing import List


class StackLayout(BaseLayout):
    def distribute_space(self, children: List[str]) -> List[str]:
        """Stack子元素增强处理"""
        enhanced = []
        for child in children:
            if child .startswith('Blank'):
                continue
            # 40%概率添加定位偏移
            if random.random() < 0.4:
                align = self._random_alignment()
                child = f"{child}.align({align})"
            # 30%概率设置zIndex（确保关键元素可见）
            if random.random() < 0.3:
                z_index = random.randint(1, 3)  # 层级范围1-3
                child = f"{child}.zIndex({z_index})"
            enhanced.append(child)
        return enhanced

    def _get_component_name(self):
        params = self._get_layout_params()
        return f"Stack({{ {', '.join(params)} }})" if params else "Stack()"

    def __init__(self):
        super().__init__()
        self.align_content = self._generate_align_content()
        self._cached_params = None

    def _generate_align_content(self):
        """生成带权重的对齐方式"""
        return _weighted_choice(
            options=Alignment,
            weights={
                Alignment.TopStart: 0.15,
                Alignment.Top: 0.1,
                Alignment.TopEnd: 0.15,
                Alignment.Center: 0.2,  # 最高概率
                Alignment.BottomStart: 0.1,
                Alignment.Bottom: 0.1,
                Alignment.BottomEnd: 0.15,
                Alignment.Start: 0.03,
                Alignment.End: 0.02
            }
        ).value

    def _random_alignment(self):
        """生成子元素对齐方式（与容器对齐形成差异）"""
        return _weighted_choice(
            options=Alignment,
            weights={
                Alignment.TopStart: 0.2,
                Alignment.BottomEnd: 0.2,
                Alignment.Center: 0.3,
                Alignment.Top: 0.1,
                Alignment.Bottom: 0.1,
                Alignment.Start: 0.05,
                Alignment.End: 0.05
            }
        ).value

    def _get_layout_params(self):
        """生成容器布局参数"""
        if not self._cached_params:
            params = []
            # 必选对齐参数
            params.append(f"alignContent: {self.align_content}")


            self._cached_params = params
        return self._cached_params

    def _get_method_chain(self):
        """支持链式调用扩展"""
        methods = []
        # 50%概率设置背景色
        if random.random() < 0.5:
            methods.append(".backgroundColor('#f0f0f0')")
        return methods