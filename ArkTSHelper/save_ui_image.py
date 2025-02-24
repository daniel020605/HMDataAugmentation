import os
import json
import time
from PIL import Image
from NJUBoxHleper.NJUBoxUploader import upload_image

# 当前存放已经提取出的UI函数的位置
UICodeDir = '.\\ArkTS_UICode'
# 需要将UI图片和代码对存入的新地址
UI_UICodeDir = '.\\ArkTS_UI_UICode'


def load_existing_json(repo_name):
    """
    加载指定仓库的提取函数的 JSON 文件。
    :param repo_path: 仓库路径
    :return: JSON 内容，若文件不存在则返回空字典
    """
    json_file_path = os.path.join(UICodeDir, f'{repo_name}_extracted_functions.json')

    if not os.path.exists(json_file_path):
        print(f"警告：仓库 '{repo_name}' 的 JSON 文件未找到，返回空数据。")
        return {}

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 JSON 文件时出错: {e}")
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
            print(f"已更新 JSON 文件: {json_file_path}")
        else:
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"已创建新 JSON 文件: {json_file_path}")
    except Exception as e:
        print(f"保存到 JSON 文件时出错 {json_file_path}: {e}")


def get_all_pages(json_data):
    """从给定的 JSON 数据中提取所有页面名称并返回一个映射关系"""
    pages_map = {}

    try:
        for page_path, functions in json_data.items():
            page_name = page_path
            pages_map[page_name] = functions
    except Exception as e:
        print(f"处理 JSON 数据时出错: {e}")

    return pages_map


def watch_new_images(image_folder, json_data, repo_name):
    """监听指定目录下的图片，并进行处理"""
    existing_images = set(os.listdir(image_folder))
    pages_map = get_all_pages(json_data)

    while True:
        try:
            current_images = set(os.listdir(image_folder))
            new_images = current_images - existing_images

            if new_images:
                for image_file in new_images:
                    if not image_file.lower().endswith('.png'):
                        continue

                    image_path = os.path.join(image_folder, image_file)
                    print(f"检测到新图片: {image_file}")
                    print("请选择一个页面，从以下列表中选择：")

                    pages = list(pages_map.keys())
                    for idx, page in enumerate(pages):
                        print(f"{idx + 1}. {page}")

                    choice = input("请输入页面的编号: ")
                    try:
                        page_name = pages[int(choice) - 1]
                    except (ValueError, IndexError) as e:
                        print(f"无效的选择，跳过此图片。错误: {e}")
                        continue

                    image_name = page_name.split('\\')[-1].replace('.ets', '')
                    new_image_name = f"{image_name}.png"
                    print(f"重命名后的图片名: {new_image_name}")
                    new_image_path = os.path.join(image_folder, new_image_name)

                    try:
                        os.rename(image_path, new_image_path)
                        print(f"图片已重命名为: {new_image_name}")
                    except Exception as e:
                        print(f"重命名图片 {image_file} 时出错: {e}")
                        continue

                    try:
                        # 上传图片
                        repo_id = "12392bc3-9aff-4f5d-b823-77f4f69113c7"  # 替换为你的仓库ID
                        parent_dir = "/"
                        relative_directory = f"鸿蒙UI截图/{repo_name}"  # 设置你希望上传到的目标目录
                        url = upload_image(new_image_path, repo_id, parent_dir, relative_directory)
                        print(f"图片上传成功，URL: {url}")
                    except Exception as e:
                        print(f"上传图片 {new_image_name} 时出错: {e}")
                        continue

                    # 删除原来的图片
                    try:
                        os.remove(new_image_path)
                        print(f"删除原始图片: {new_image_name}")
                    except Exception as e:
                        print(f"删除图片 {new_image_name} 时出错: {e}")

                    # 构造数据
                    try:
                        data = {url: pages_map[page_name]}
                        save_to_json(os.path.join(UI_UICodeDir, f'{repo_name}_code_URL.json'), data)
                        print(f"已更新 {page_name} 与新的图片 URL。")
                    except Exception as e:
                        print(f"保存 URL 数据时出错 {page_name}: {e}")

            existing_images = current_images

            # 等待 1 秒钟后再次检测
            time.sleep(1)

        except Exception as e:
            print(f"图片处理循环出错: {e}")
            time.sleep(5)  # 防止程序因异常退出，稍作延迟后继续


def process_repo_images(repo_path, image_folder):
    """
    处理指定仓库的 UI 图片，并将图像与页面功能信息保存到 JSON 文件中。
    :param repo_path: 仓库路径
    :param image_folder: 存放图片的文件夹路径
    """
    try:
        repo_name = os.path.basename(repo_path)
        # 加载 JSON 文件
        json_data = load_existing_json(repo_name)

        if json_data:  # 如果 JSON 文件成功加载
            watch_new_images(image_folder, json_data, repo_name)
        else:
            print(f"错误: 无法加载仓库 '{repo_name}' 的 JSON 数据。退出。")
    except Exception as e:
        print(f"处理仓库图片时出错: {e}")


if __name__ == "__main__":
    try:
        repo_path = r'C:\Users\sunguyi\Desktop\repos\github_5min_stars_projects\harmony-next-music-sharing_1'
        image_folder = r"C:\Users\sunguyi\Desktop\repos\UIPictures"

        # 调用提取后的函数
        process_repo_images(repo_path, image_folder)
    except Exception as e:
        print(f"主函数中出错: {e}")
