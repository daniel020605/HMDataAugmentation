import os
import re
from datetime import datetime


def update_arkts_project(code_snippet, project_path="./existing_project", component_name="TestComponent"):
    """
    在现有项目基础上进行代码热更新
    :param code_snippet: 包含以下键的字典
        - "variables" (列表)
        - "solution" (字符串)
    :param project_path: 现有项目路径
    :param component_name: 要修改的组件名称
    """
    ets_path = os.path.join(project_path, "entry/src/main/ets/pages/Index.ets")

    if not os.path.exists(ets_path):
        print(f"❌ 目标文件不存在：{ets_path}")
        return

    try:
        with open(ets_path, "r+", encoding="utf-8") as f:
            content = f.read()

            # 执行代码替换
            new_content = perform_code_replacement(content, code_snippet, component_name)

            # 回写文件
            f.seek(0)
            f.write(new_content)
            f.truncate()

        print(f"✅ 代码热更新成功：{ets_path}")
        print("建议立即在DevEco Studio中执行以下操作：")
        print("1. 点击顶部菜单 Build > Clean Project")
        print("2. 点击运行按钮重新编译")

    except Exception as e:
        print(f"❌ 文件操作失败：{str(e)}")


def perform_code_replacement(original_content, code_snippet, component_name):
    """执行智能代码替换"""
    # 替换变量声明
    vars_pattern = re.compile(
        r'(@State\s+apiItems:\s*TestApi\[\]\s*=\s*initHotspotManagerApIData\(\)\s*)\n',
        re.DOTALL
    )
    updated_content = vars_pattern.sub(
        '\n'.join(code_snippet['variables']) + '\n',
        original_content
    )

    # 替换解决方案方法
    method_pattern = re.compile(
        r'(getCurrentState\(index: number\)\s*\{[\s\S]*?\}\s*)\n',
        re.DOTALL
    )
    updated_content = method_pattern.sub(
        code_snippet['solution'] + '\n',
        updated_content
    )

    # 更新组件名称（可选）
    if component_name != "TestComponent":
        component_pattern = re.compile(
            r'@Component\s*struct\s*\w+',
            re.DOTALL
        )
        updated_content = component_pattern.sub(
            f'@Component struct {component_name}',
            updated_content
        )

    # 添加版本标记
    version_comment = f'// 最后更新于：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    return version_comment + updated_content


# 使用示例
if __name__ == "__main__":
    user_code = {
        "variables": [
            "@State apiItems: TestApi[] = initHotspotManagerApIData() // 修改后的状态变量"
        ],
        "solution": """getCurrentState(index: number) {
    // 新增调试语句
    console.log(`正在获取索引 ${index} 的状态`);
    return this.apiItems[index].result;
  }"""
    }

    update_arkts_project(user_code)