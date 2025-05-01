import os
import json
from NJUBoxHelper.NJUBoxUploader import upload_image

# 当前存放已经提取出的UI函数的位置
UICodeDir = '.\\ArkTS_UICode'
# 需要将UI图片和代码对存入的新地址
UI_UICodeDir = '.\\ArkTS_UI_UICode'


def load_existing_json(repo_name):
    """
    加载指定仓库的提取函数的 JSON 文件。
    :param repo_name: 仓库名
    :return: JSON 内容，若文件不存在则返回空字典
    """
    json_file_path = os.path.join(UICodeDir, f'{repo_name}_extracted_functions.json')

    if not os.path.exists(json_file_path):
        print(f"Warning: JSON file for repo '{repo_name}' not found. Returning empty data.")
        return {}

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return {}


def save_to_json(json_file_path, data):
    """将新的界面和代码对保存到 JSON 文件"""
    os.makedirs(UI_UICodeDir, exist_ok=True)

    try:
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            existing_data.update(data)

            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            print(f"Updated existing JSON file: {json_file_path}")
        else:
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Created new JSON file: {json_file_path}")
    except Exception as e:
        print(f"Error saving to JSON file {json_file_path}: {e}")


def save_image_and_code(image_path, code, repo_name):
    """上传图片并保存代码"""
    try:
        print(f"上传图片 {image_path}...")
        repo_id = "12392bc3-9aff-4f5d-b823-77f4f69113c7"  # 替换为你的仓库ID
        parent_dir = "/"
        relative_directory = f"鸿蒙UI截图/{repo_name}"  # 设置你希望上传到的目标目录
        url = upload_image(image_path, repo_id, parent_dir, relative_directory)
        print(f"图片上传成功，URL: {url}")

        # 保存图片和代码对
        data = {
            url: [
                {
                    "function_name": "build",
                    "content": code
                }
            ]
        }
        save_to_json(os.path.join(UI_UICodeDir, f'{repo_name}_code_URL.json'), data)
        print(f"图片URL和代码已保存到JSON文件")

    except Exception as e:
        print(f"保存图片和代码时出错: {e}")


def manual_input_save_image_data():
    # 提示用户输入图片路径和仓库名
    image_path = input("图片路径: ").strip()
    repo_name = input("仓库名: ").strip()

    # 确保输入路径有效
    if not os.path.exists(image_path):
        print(f"错误：图片文件 '{image_path}' 不存在，请提供有效路径。")
        return
    # 创建一个新的txt文件，提示用户填写代码

    code_file_path = './UICode_manual_code.txt'
    try:
        # 创建文件并提示用户输入代码
        with open(code_file_path, 'w', encoding='utf-8') as file:
            file.write("")  # 确保文件为空，若文件已存在将清空文件内容

        print(f"请将代码保存到文件 '{code_file_path}' 中。")
        print("在此文件中输入或粘贴代码，然后保存文件。")
        input("保存完代码后，请按 Enter 继续...")

        # 等待用户确认并读取文件内容
        if os.path.exists(code_file_path):
            try:
                with open(code_file_path, 'r', encoding='utf-8') as file:
                    code = file.read().strip()

                if code:
                    print(f"接收到的代码为：\n{code}")
                    # 请求用户输入新的图片名称
                    new_image_name = input("请输入新的图片名称（不包括扩展名）: ").strip()
                    if not new_image_name:
                        print("错误：图片名称不能为空！")
                        return

                    # 构造新的图片路径
                    image_name = os.path.basename(image_path)
                    file_extension = os.path.splitext(image_name)[-1]  # 获取文件扩展名
                    new_image_path = os.path.join(os.path.dirname(image_path), f"{new_image_name}{file_extension}")

                    # 给图片改名
                    try:
                        os.rename(image_path, new_image_path)
                        print(f"图片已重命名为: {new_image_name}{file_extension}")
                        image_path = new_image_path  # 更新图片路径
                    except Exception as e:
                        print(f"图片重命名失败: {e}")
                        return
                    save_image_and_code(image_path, code, repo_name)
                else:
                    print("文件为空，请在文件中输入有效的代码。")

            except Exception as e:
                print(f"读取文件时出错：{e}")
        else:
            print(f"错误：文件 '{code_file_path}' 不存在，请确保将代码保存到该文件。")

    finally:
        # 删除临时创建的代码文件
        if os.path.exists(code_file_path):
            try:
                os.remove(code_file_path)
                print(f"已删除临时文件 '{code_file_path}'")
            except Exception as e:
                print(f"删除临时文件时出错：{e}")


def process_repo_images():
    """
    处理指定仓库的 UI 图片，并将图像与页面功能信息保存到 JSON 文件中。
    """
    try:
        # 调用手动输入的函数处理图片和代码
        manual_input_save_image_data()

    except Exception as e:
        print(f"处理仓库图片时出错: {e}")


if __name__ == "__main__":
    try:
        # 调用手动输入的函数处理图片和代码
        process_repo_images()

    except Exception as e:
        print(f"主函数出错: {e}")
