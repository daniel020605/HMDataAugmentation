import os
import shutil

from ArkTSHelper.autoRunner.failedFileDeleter import is_fail
root_floder = '/Users/jiaoyiyang/harmonyProject/repos/combined_failed'

target_root = '/Users/jiaoyiyang/harmonyProject/repos/combined_collected'
fail_root = '/Users/jiaoyiyang/harmonyProject/repos/combined_failed'

dead_root =  '/Users/jiaoyiyang/harmonyProject/repos/combined_dead'



def process_ets_files(root_dir):
    """处理ETS文件并执行自动化流程"""
    success =0
    fail = 0
    for subdir, _, files in os.walk(root_dir):
        if subdir == root_dir:
            continue

        ets_files = [f for f in files if f.endswith('.ets')]
        target_screenshot = os.path.join(subdir, f"{os.path.basename(subdir)}_screenshot.png")

        if len(ets_files) == 1 and os.path.exists(target_screenshot):
            try:
                # 提取子目录名称
                subdir_name = os.path.basename(subdir)
                target_path = os.path.join(target_root, subdir_name)
                fail_path = os.path.join(fail_root, subdir_name)
                dead_path = os.path.join(dead_root, subdir_name)

                if os.path.exists(target_path) or (os.path.exists(fail_path) and root_floder != fail_root) or os.path.exists(dead_path):
                    print(f"已存在 {target_path}")
                    continue

                if not is_fail(target_screenshot):
                    if not root_floder == fail_root:
                        # 复制整个目录（包含所有子目录和文件）
                        shutil.copytree(subdir, target_path)
                        success += 1
                        print(f"已复制 {subdir_name} 到 {target_root}")
                    else:
                        shutil.move(subdir, target_path)
                        success += 1
                        print(f"已移动 {subdir_name} 到 {target_root}")

                else:
                    if not root_floder == fail_root:
                        shutil.copytree(subdir, fail_path)
                        fail += 1
                        print(f"已复制失败 {subdir_name} 到 {fail_path}")
                    else:
                        shutil.move(subdir, dead_path)
                        fail += 1
                        print(f"已移动失败 {subdir_name} 到 {dead_path}")

            except FileNotFoundError as e:
                print(f"源目录不存在: {subdir}")
            except PermissionError:
                print(f"权限不足，无法操作 {subdir}")
            except Exception as e:
                print(f"未知错误: {str(e)}")
    print(f"共成功 {success} 个文件夹")
    print(f"共失败 {fail} 个文件夹")


if __name__ == '__main__':
    process_ets_files(root_floder)