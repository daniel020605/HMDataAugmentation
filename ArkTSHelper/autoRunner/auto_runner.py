
import shutil

SINGLE_FILE_PROJECTS_DIR = r"/Users/jiaoyiyang/harmonyProject/repos/combined_failed"
EMPTY_PROJECT_INDEX_PATH = r"/Users/jiaoyiyang/harmonyProject/repos/emptyProject/entry/src/main/ets/pages/Index.ets"
SCREENSHOT_OUTPUT_DIR = r"/Users/jiaoyiyang/harmonyProject/repos/UIPictures"
IMG_PATH = r"/Users/jiaoyiyang/harmonyProject/repos/emptyProject/entry/src/main/resources/base/media"

import pyautogui
import os
import subprocess
import time

AUTO = True
BUTTON_COORDINATES = [
    (800, 52),
    (1370, 375),
    (1300, 520)
]

def run_deveco_project():
    """运行Deveco项目的示例函数（需要根据实际环境修改）"""
    print("正在运行Deveco项目...")
    try:
        if AUTO:
            pyautogui.click(BUTTON_COORDINATES[0][0], BUTTON_COORDINATES[0][1])
            time.sleep(3.5)

    except subprocess.CalledProcessError as e:
        print(f"运行失败: {e}")
    except FileNotFoundError:
        print("未找到命令行工具，请确保环境变量配置正确。")


def take_screenshot(output_folder,timeout=600, interval=0.5):
    """
    轮询指定文件夹，直到检测到新截图文件出现为止。

    :param output_folder: 截图保存的文件夹路径
    :param timeout: 超时时间（秒），默认为600秒
    :param interval: 轮询间隔时间（秒），默认为0.5秒
    :return: 新截图文件的路径，如果超时则返回None
    """
    # 获取文件夹中已有的文件列表
    initial_files = set(os.listdir(output_folder))

    print(f"开始轮询，等待新截图出现...")
    if AUTO:
        pyautogui.click(BUTTON_COORDINATES[1][0], BUTTON_COORDINATES[1][1])
        time.sleep(0.5)
        pyautogui.click(BUTTON_COORDINATES[2][0], BUTTON_COORDINATES[2][1])
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 获取当前文件夹中的文件列表
        current_files = set(os.listdir(output_folder))

        # 找出新文件
        new_files = current_files - initial_files

        if new_files:
            # 假设只有一个新文件
            time.sleep(0.5)
            new_file = new_files.pop()
            new_file_path = os.path.join(output_folder, new_file)
            print(f"检测到新截图")
            return new_file_path

        # 等待一段时间后再次检查
        time.sleep(interval)

    print(f"超时，未检测到新截图。")
    return None


def list_subdirectories(root_dir):
    """只遍历指定目录的直接子文件夹"""
    try:
        entries = os.listdir(root_dir)

        subdirs = [entry for entry in entries if os.path.isdir(os.path.join(root_dir, entry))]

        return subdirs
    except Exception as e:
        print(f"读取目录失败: {e}")
        return []


def process_ets_files(root_dir, index_ets_path):
    """处理ETS文件并执行自动化流程"""
    count = -1
    for subdir, _, files in os.walk(root_dir):
        if subdir == root_dir:
            continue
        count += 1
        ets_files = [f for f in files if f.endswith('.ets')]
        target_screenshot = os.path.join(subdir, f"{os.path.basename(subdir)}_screenshot.png")

        if len(ets_files) == 1 and not os.path.exists(target_screenshot):
            ets_file_path = os.path.join(subdir, ets_files[0])

            # 更新index.ets文件
            with open(ets_file_path, 'r', encoding='utf-8') as ets_file:
                ets_content = ets_file.read()

            with open(index_ets_path, 'w', encoding='utf-8') as index_file:
                index_file.write(ets_content)

            # 处理图片文件并记录已复制的文件
            copied_files = []
            for file in files:
                file_path = os.path.join(subdir, file)
                # 排除截图文件并检查图片格式
                if (file.lower().endswith(('.png', '.jpg', '.svg', '.gif', '.bmp'))
                        and not file.endswith('_screenshot.png')):
                    try:
                        if not os.path.exists(IMG_PATH):
                            os.makedirs(IMG_PATH)
                        dest_path = os.path.join(IMG_PATH, file)
                        shutil.copy(file_path, dest_path)
                        copied_files.append(dest_path)  # 记录完整目标路径
                        print(f"Copied {file} to {IMG_PATH}")
                    except Exception as e:
                        print(f"Error copying file {file}: {e}")

            print(f"已将{os.path.basename(subdir)}中的内容写入index.ets")

            # 运行项目并截图
            run_deveco_project()
            screenshot_path = take_screenshot(SCREENSHOT_OUTPUT_DIR)

            if not screenshot_path:
                print(f"截图失败，跳过文件夹 {subdir}")
                # 清理复制的图片
                for copied_file in copied_files:
                    try:
                        os.remove(copied_file)
                        print(f"清理临时文件: {copied_file}")
                    except Exception as e:
                        print(f"清理失败: {e}")
                continue

            # 移动并重命名截图
            try:
                os.rename(screenshot_path, target_screenshot)
                print(f"截图已保存至: {target_screenshot}")
            except Exception as e:
                print(f"移动截图失败: {e}")

            # 检查index.ets是否被修改并写回原文件
            with open(index_ets_path, 'r', encoding='utf-8') as index_file:
                current_content = index_file.read()
                if current_content != ets_content:
                    with open(ets_file_path, 'w', encoding='utf-8') as ets_file:
                        ets_file.write(current_content)
                    print("已同步修改后的index.ets内容")

            # 最终清理复制的图片（无论成功与否）
            for copied_file in copied_files:
                try:
                    os.remove(copied_file)
                except Exception as e:
                    print(f"清理临时文件失败: {e}")
            print(f"已清理临时图片文件")
    print(f"共处理 {count} 个文件夹")

def main():
    print("请打开Deveco运行界面")
    if AUTO:
        time.sleep(5)
    process_ets_files(SINGLE_FILE_PROJECTS_DIR, EMPTY_PROJECT_INDEX_PATH)

if __name__ == "__main__":
    main()