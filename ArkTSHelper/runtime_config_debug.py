import os
import json5
import shutil
from pathlib import Path

REPLACE_RULES = {
    10: "4.0.0(10)",
    12: "5.0.0(12)",
    "OpenHarmony": "HarmonyOS"
}

##用于修改build-profile.json5文件中的compileSdkVersion和runtimeOS字段以方便运行
def needs_modification(app_data):
    """检查是否符合修改条件"""
    if not isinstance(app_data, dict):
        return False

    products = app_data.get("products")
    if not isinstance(products, list):
        return False

    for product in products:
        if not isinstance(product, dict):
            continue

        # 检查 compileSdkVersion 和 runtimeOS
        cv = product.get("compileSdkVersion")
        ros = product.get("runtimeOS")
        if cv in (10, 12) and ros == "OpenHarmony":
            return True

    return False


def modify_products(app_data):
    """执行结构化修改"""
    for product in app_data.get("products", []):
        if not isinstance(product, dict):
            continue

        # 删除 compileSdkVersion
        if "compileSdkVersion" in product:
            del product["compileSdkVersion"]

        # 替换 compatibleSdkVersion
        csv = product.get("compatibleSdkVersion")
        if csv in REPLACE_RULES:
            product["compatibleSdkVersion"] = REPLACE_RULES[csv]

        # 替换 runtimeOS
        if product.get("runtimeOS") == "OpenHarmony":
            product["runtimeOS"] = REPLACE_RULES["OpenHarmony"]

    return app_data


def process_file(file_path):
    """处理单个文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json5.load(f)

        # 调试：打印文件内容
        print(f"文件内容: {json5.dumps(data, indent=2)}")

        # 检查是否需要修改
        app_data = data.get("app")
        if not needs_modification(app_data):
            print(f"文件 {file_path} 不符合修改条件")
            return False

        # 执行修改
        modified_app = modify_products(app_data)
        data["app"] = modified_app

        # 创建备份
        backup_path = file_path.with_suffix(".json5.bak")
        shutil.copyfile(file_path, backup_path)

        # 写入修改
        with open(file_path, "w", encoding="utf-8") as f:
            json5.dump(data, f, indent=2, quote_keys=True, trailing_commas=False)

        return True
    except Exception as e:
        print(f"处理 {file_path} 失败: {str(e)}")
        return False


def process_root_folder(root_dir):
    """处理根目录"""
    processed = 0
    errors = 0

    for entry in os.listdir(root_dir):
        subdir = Path(root_dir) / entry
        if subdir.is_dir():
            target_file = subdir / "build-profile.json5"
            if target_file.exists():
                print(f"正在处理: {target_file}")
                if process_file(target_file):
                    processed += 1
                else:
                    errors += 1

    print(f"\n处理完成！成功: {processed}, 失败: {errors}")


if __name__ == "__main__":
    root_directory = "C:/Users/sunguyi/Desktop/repos/gitee_5min_stars_projects"
    process_root_folder(root_directory)