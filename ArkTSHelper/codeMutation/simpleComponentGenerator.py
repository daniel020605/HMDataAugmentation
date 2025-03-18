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
        return []

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
        return []

    def generate(self):
        styles = [
            f"color({random_color()})",
            f"strokeWidth({random.randint(1, 3)})",
            f"margin({{ {random_margin()} }})"
        ]
        return apply_styles("Divider()", styles)


class EditableTitleBarGenerator(ComponentGenerator):
    @property
    def imports(self):
        return [
            "EditableTitleBar",
            "EditableLeftIconType",
            "promptAction",
            "LengthMetrics",
        ]

    def generate(self):
        params = []

        # leftIconStyle (必填)
        left_icon = random.choice([
            "EditableLeftIconType.Back",
            "EditableLeftIconType.Cancel"
        ])
        params.append(f"leftIconStyle: {left_icon}")

        # title (必填)
        title = random.choice([
            "编辑页面", "主标题", "设置", "个人资料", "新建项目"
        ])
        params.append(f"title: '{title}'")

        # subtitle (可选)
        if random.random() < 0.5:
            subtitle = random.choice([
                "副标题", "详细信息", "配置选项", "草稿"
            ])
            params.append(f"subtitle: '{subtitle}'")

        # imageItem (可选)
        if random.random() < 0.3:
            image_value = random.choice([
                "$r('sys.media.ohos_ic_normal_white_grid_image')",
                "$r('app.media.app_icon')"
            ])
            is_enabled = random.choice(['true', 'false'])
            action = "() => { promptAction.showToast({ message: '头像点击' }) }"
            image_item = f"{{ value: {image_value}, isEnabled: {str(is_enabled).lower()}, action: {action} }}"
            params.append(f"imageItem: {image_item}")

        # menuItems (可选)
        menu_items = []
        for _ in range(random.randint(0, 2)):
            value = random.choice([
                "$r('sys.media.ohos_ic_public_cancel')",
                "$r('sys.media.ohos_ic_public_remove')",
                "$r('sys.media.ohos_ic_public_add')"
            ])
            label = random.choice(["删除", "取消", "添加"]) if random.random() < 0.5 else None
            is_enabled = random.choice(['true', 'false'])
            action = "() => { promptAction.showToast({ message: '菜单项点击' }) }"
            menu_item = "{ value: " + value
            if label:
                menu_item += f", label: '{label}'"
            menu_item += f", isEnabled: {str(is_enabled).lower()}, action: {action} }}"
            menu_items.append(menu_item)
        if menu_items:
            params.append(f"menuItems: [{', '.join(menu_items)}]")

        # isSaveIconRequired (必填)
        params.append(f"isSaveIconRequired: {random.choice(['true', 'false'])}")

        # 事件回调
        if random.random() < 0.5:
            params.append("onSave: () => { promptAction.showToast({ message: '保存成功' }) }")

        # options (必填)
        options = []
        if random.random() < 0.7:
            options.append(f"backgroundColor: {random_color()}")
        if random.random() < 0.5:
            options.append(f"backgroundBlurStyle: {random.choice(['BlurStyle.COMPONENT_THICK', 'BlurStyle.NONE'])}")
        # safeArea配置
        if random.random() < 0.5:
            options.append("safeAreaTypes: [SafeAreaType.SYSTEM]")
        if random.random() < 0.5:
            options.append("safeAreaEdges: [SafeAreaEdge.TOP]")
        params.append(f"options: {{ {', '.join(options)} }}")

        # contentMargin (可选)
        if random.random() < 0.3:
            start = random.randint(20, 50)
            end = random.randint(20, 50)
            params.append(
                f"contentMargin: {{ start: LengthMetrics.vp({start}), end: LengthMetrics.vp({end}) }}"
            )

        return f"EditableTitleBar({{ {', '.join(params)} }})"


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


class SelectTitleBarGenerator(ComponentGenerator):
    @property
    def imports(self):
        return [
            "SelectTitleBar",
            "promptAction",
            "SelectTitleBarMenuItem"
        ]

    def generate(self):
        params = []

        # 必填参数
        # options生成
        option_templates = [
            ["所有照片", "本地（设备）", "本地储存卡）"],
            ["最新消息", "未读消息", "已归档"],
            ["全部文件", "图片", "视频", "文档"]
        ]
        options = [f"{{ value: '{item}' }}"
                   for item in random.choice(option_templates)]
        params.append(f"options: [{', '.join(options)}]")

        # selected生成（基于options长度）
        selected_index = random.randint(0, len(options) - 1)
        params.append(f"selected: {selected_index}")

        # 可选参数
        # subtitle
        if random.random() < 0.4:
            subtitles = [
                "example@example.com",
                "未读消息 5条",
                f"最后更新：2024-0{random.randint(1, 9)}-0{random.randint(1, 9)}",
                "存储空间 85%"
            ]
            params.append(f"subtitle: '{random.choice(subtitles)}'")

        # menuItems
        if random.random() < 0.6:
            icons = [
                "$r('sys.media.ohos_save_button_filled')",
                "$r('sys.media.ohos_ic_public_copy')",
                "$r('sys.media.ohos_ic_public_edit')",
                "$r('sys.media.ohos_ic_public_remove')"
            ]
            menu_items = []
            for _ in range(random.randint(1, 3)):
                menu_item = [
                    f"value: {random.choice(icons)}",
                    f"isEnabled: {random.choice(['true', 'false'])}"
                ]
                if random.random() < 0.3:
                    menu_item.append("action: () => promptAction.showToast({ message: '菜单点击' })")
                menu_items.append("{ " + ", ".join(menu_item) + " }")
            params.append(f"menuItems: [{', '.join(menu_items)}]")

        # badgeValue
        if random.random() < 0.3:
            badge = random.choice([
                random.randint(1, 99),
                random.randint(100, 200),  # 测试超大数值情况
                random.choice([0, -1])  # 测试不显示情况
            ])
            params.append(f"badgeValue: {badge}")

        # hidesBackButton
        if random.random() < 0.4:
            params.append(f"hidesBackButton: {random.choice(['true', 'false'])}")

        # 事件处理
        if random.random() < 0.7:
            params.append(
                "onSelected: (index) => promptAction.showToast({ message: `选中索引: ${index}` })"
            )

        return f"SelectTitleBar({{ {', '.join(params)} }})"


# --------------------------
# 组件注册表
# --------------------------
GENERATOR_CLASSES = [
    BlankGenerator,
    TextGenerator,
    TextGenerator,
    DividerGenerator
]
TOP_GENERATOR_CLASSES = [
    BlankGenerator,
    TextGenerator,
    TextGenerator,
    EditableTitleBarGenerator,
    SelectTitleBarGenerator
]


def create_generator(pos = 'normal') -> ComponentGenerator:
    """创建随机组件生成器"""
    if pos == 'Top':
        return random.choice(TOP_GENERATOR_CLASSES)()
    else:
        return random.choice(GENERATOR_CLASSES)()



if __name__ == '__main__':
    # 生成10个不同组件
    for _ in range(10):
        code  = create_generator().generate()
        print(f"生成组件：{code}")