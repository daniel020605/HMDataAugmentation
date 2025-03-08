import os
import json
from openai import OpenAI

# 配置DeepSeek API
client = OpenAI(
    api_key="",  # 替换为你的实际API Key
    base_url="https://api.deepseek.com"
)

# 配置路径和提示词
input_dir = "./components"
output_dir = "./answers"
user_prompt = """请根据以下组件文档内容：
----------------------------
{}
----------------------------
提供覆盖该组件所有功能的ArkTS示例代码，要求：
1. 按JSON格式输出，键名使用功能描述命名
2. 每个示例必须包含完整的代码结构（@Entry/@Component）
3. 不同示例展示不同使用场景
4. 使用双引号包裹字符串，不要包含注释
5. 图片路径统一使用 "common/images/example.png"
6. 每个代码段应能直接编译运行

示例格式：
{{ 
    "xxx": "@Entry\\n@Component\\nstruct Index {{ ... }}",
    "xxx": "@Entry\\n@Component\\nstruct CustomComponent {{ ... }}"
}}
"""


def validate_json(json_str: str) -> bool:
    """验证JSON格式有效性"""
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False


# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 遍历处理所有txt文件
for filename in os.listdir(input_dir):
    if not filename.endswith(".txt"):
        continue

    file_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, f"analysis_{filename}")

    if os.path.exists(output_path):
        print(f"跳过已处理文件：{filename}")
        continue

    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            print(f"跳过空文件：{filename}")
            continue

        # 构造完整提示（已转义花括号）
        full_prompt = user_prompt.format(content)

        # API调用
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是鸿蒙系统ArkTS语言专家，专注于生成规范的代码示例"},
                {"role": "user", "content": full_prompt},
            ],
            temperature=0.3,  # 降低随机性保证代码规范
            stream=False
        )

        # 处理响应
        raw_answer = response.choices[0].message.content

        # 提取JSON部分（处理可能的多余文本）
        start_idx = raw_answer.find('{')
        end_idx = raw_answer.rfind('}') + 1
        json_str = raw_answer[start_idx:end_idx]

        # 验证JSON格式
        if not validate_json(json_str):
            raise ValueError("返回内容不符合JSON格式")

        # 格式化输出
        formatted_answer = f"// 组件分析报告：{filename}\n" + \
                           "// 自动生成代码示例 - 请验证后使用\n\n" + \
                           json.dumps(json.loads(json_str), indent=2, ensure_ascii=False)

        # 保存结果
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_answer)

        print(f"成功处理：{filename}")

    except Exception as e:
        print(f"处理失败 [{filename}]：{str(e)}")
        # 写入错误日志
        with open(os.path.join(output_dir, "error.log"), "a") as f:
            f.write(f"[{filename}] {str(e)}\n")

print("\n处理完成！有效结果保存在:", os.path.abspath(output_dir))