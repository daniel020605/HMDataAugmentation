from ArkTSHelper.extract_ui_code import extract_functions_from_project
from ArkTSHelper.save_ui_image import process_repo_images

project_path = r'C:\Users\sunguyi\Desktop\repos\gitee_5min_stars_projects\demo_1'
image_folder = r"C:\Users\sunguyi\Desktop\repos\UIPictures"

if __name__ == '__main__':
    # 从项目中提取函数
    extract_functions_from_project(project_path)

    # 处理 UI 图片
    process_repo_images(project_path, image_folder)