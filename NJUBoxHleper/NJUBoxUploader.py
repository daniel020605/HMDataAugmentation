from NJUBoxHleper.NJUBoxClient import NJUBoxClient
import os
# 配置初始化参数
NJU_ID = "211250095"  # 替换成你自己的 NJU ID
AUTH_SERVER_PASSWORD = "8006CHYhaha789"  # 替换成你自己的 AUTH SERVER PASSWORD
WEB_APP_NAME = "车昊宇 211250095"  # 替换成你自己的 WEB APP NAME


# 初始化 NJUBox 客户端
njuClient = NJUBoxClient(NJU_ID, AUTH_SERVER_PASSWORD, WEB_APP_NAME)

def upload_image(file_path, repo_id, parent_dir, relative_directory):
    """
    上传图片到 NJUBox
    :param file_path: 本地图片路径
    :param repo_id: 仓库 ID
    :param parent_dir: 上传到仓库中的目标目录
    :param filename: 上传后保存的文件名
    :return: 上传链接
    """

    file_path = file_path.replace("\\", "/")

    # 上传图片
    with open(file_path, 'rb') as file:
        response = njuClient.uploadFile(file_path, repo_id, parent_dir, relative_directory)
        file_url = njuClient.downloadFile(repo_id, relative_directory + '/'+ file_path.split('/')[-1], "JUSTURL")
        return file_url

if __name__ == "__main__":
    # 设置你要上传的图片文件路径
    image_path = "C:\\Users\\sunguyi\\Desktop\\repos\\UIPictures"  # 替换成你实际的图片路径
    repo_id = "12392bc3-9aff-4f5d-b823-77f4f69113c7"  # 替换为你的仓库ID
    parent_dir = "/"
    relative_directory = "鸿蒙UI截图"  # 设置你希望上传到的目标目录

    # 上传图片
    upload_url = upload_image(image_path, repo_id, parent_dir, relative_directory)

    # 打印上传的图片 URL
    if upload_url:
        print(f"Access your uploaded image at: {upload_url}")