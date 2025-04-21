import os
import re
import shutil


from PIL import Image
import imagehash

# ====================== 参数配置区域 ======================
# 在这里直接修改参数值
reference_image = "/Users/jiaoyiyang/harmonyProject/code/HMDataAugmentation/ArkTSHelper/autoRunner/targetButton/failed.png"  # 参考图片路径
target_dir = "/Users/jiaoyiyang/harmonyProject/repos/combined_failed"  # 要扫描的目标文件夹
hash_size = 8  # 哈希尺寸 (8/16/32)
hash_threshold = 5  # 允许的哈希差异阈值
dry_run = False


# ========================================================

def calculate_phash(image_path):
    """计算图像的感知哈希"""
    try:
        with Image.open(image_path) as img:
            return imagehash.phash(img, hash_size=hash_size)
    except Exception as e:
        print(f"无法处理图像 {image_path}: {str(e)}")
        return None


def find_matching_folders():
    """查找匹配文件夹"""
    matches = []

    ref_hash = calculate_phash(reference_image)

    if ref_hash is None:
        return matches

    print(f"\n参考图片哈希: {ref_hash}")
    print(f"相似度阈值: 差异 ≤ {hash_threshold}")

    for root, dirs, files in os.walk(target_dir):
        folder_name = os.path.basename(root)
        print(f"\n扫描文件夹: {root}")
        # pattern = r'\d{6}$'
        # if bool(re.search(pattern, folder_name)):
        #     matches.append(root)
        #     continue
        for f in files:
            if f.lower().startswith(folder_name.lower()) and f.lower().endswith('.png'):
                file_path = os.path.join(root, f)
                file_hash = calculate_phash(file_path)

                if file_hash and (ref_hash - file_hash) <= hash_threshold:
                    matches.append(file_path)
                    print(f"❗ 匹配到目标文件夹: {root}")
                    break  # 找到即停止检查其他文件
    return matches

def is_fail(file_path):
    file_hash = calculate_phash(file_path)
    ref_hash = calculate_phash(reference_image)
    return file_hash and (ref_hash - file_hash) <= hash_threshold

def main():
    if not os.path.isfile(reference_image):
        print(f"错误: 参考图片不存在 {reference_image}")
        return

    matches = find_matching_folders()

    if not matches:
        print("\n未找到匹配文件夹")
        return

    print("\n找到以下匹配文件夹:")
    for i, path in enumerate(matches, 1):
        print(f"  {i}. {path}")

    if dry_run:
        print("\n模拟运行完成 (未实际删除)")
        return

    confirm = input("\n确认要删除这些文件夹吗？(y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return

    # 安全删除流程
    success = 0
    failure = 0
    for folder in matches:
        try:
            # 二次验证：确保文件夹仍然存在
            if not os.path.isdir(folder):
                if os.path.isfile(folder):
                    os.remove(folder)
                print(f"警告: 文件夹已不存在 {folder}")
                continue

            # 权限检查（尝试创建临时文件）
            test_file = os.path.join(folder, '.perm_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except PermissionError:
                print(f"权限不足: {folder}")
                failure += 1
                continue

            # 执行删除
            #shutil.move(folder, "/Users/jiaoyiyang/harmonyProject/repos/mutationProjects")
            shutil.rmtree(folder)  # 使用 shutil 递归删除
            print(f"成功删除: {folder}")
            success += 1

        except Exception as e:
            print(f"删除失败 [{type(e).__name__}]: {folder} - {str(e)}")
            failure += 1

    print(f"\n操作完成！成功删除 {success} 个，失败 {failure} 个")



if __name__ == "__main__":
    main()