# 安卓项目代码检查模板
import os
import subprocess

# 指定 Android 项目的路径
project_path = """C:/Users/74187/AndroidStudioProjects/MinApplication"""
object_file = project_path + "/app/src/main/res/layout/activity_main.xml"

def replace_or_create_file(file_path, content):
    """
    Replaces the content of a file. If the file does not exist, it creates a new one.

    :param file_path: Path to the file
    :param content: Content to write into the file
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Open the file in write mode and replace its content
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"File '{file_path}' has been updated successfully.")
    except Exception as e:
        print(f"Error while processing the file: {e}")

def run_command(command, cwd=None):
    """
    运行命令行工具命令并实时打印输出
    """
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        while True:
            output = process.stdout.readline()
            error = process.stderr.readline()
            if output == '' and error == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
            if error:
                print(error.strip())
        rc = process.poll()
        return rc == 0
    except Exception as e:
        print(f"Error while executing command: {e}")
        return False
def change_gradlew_permissions(project_path):
    chmod_command = f"chmod +x {project_path}/gradlew"
    return run_command(chmod_command)

def sync_project_with_gradle_files(project_path):
    print("Syncing project with Gradle files...")
    sync_command = "./gradlew --refresh-dependencies"
    return run_command(sync_command, cwd=project_path)

def run_lint_check(project_path):
    print("Running lint...")
    lint_command = "./gradlew lint"
    return run_command(lint_command, cwd=project_path)

def build_project(project_path):
    print("Building the project...")
    build_command = "./gradlew build"
    return run_command(build_command, cwd=project_path)

def check_and_build_android_project(project_path):
    if not os.path.exists(project_path):
        print(f"Error: Path {project_path} does not exist.")
        return False

    if not change_gradlew_permissions(project_path):
        print("Error while changing gradlew permissions.")
        return False

    if not sync_project_with_gradle_files(project_path):
        print("Sync failed. Please check the errors and try again.")
        return False

    if not run_lint_check(project_path):
        print("Lint failed. Please fix the issues and try again.")
        return False

    if not build_project(project_path):
        print("Build failed. Please check the errors and try again.")
        return False

    print("Sync, lint, and build completed successfully!")
    return True

def lint(file_path):
    """
    运行 lint 检查
    """
    lint_command = f"lint {file_path}"
    result = run_command(lint_command)
    if result:
        print(f"Lint check passed for {file_path}")
    else:
        print(f"Lint check failed for {file_path}")

import os

def process_xml_files(xml_files, project_path, target_file_path):
    """
    批量处理XML文件：替换模板项目中的文件内容并运行Lint检查。

    :param xml_files: 包含XML代码的列表，每个元素是一个字典，格式为 {'file_name': '文件名', 'content': 'XML内容'}
    :param project_path: 模板项目的路径
    :param target_file_path: 模板项目中目标文件的相对路径
    """
    for xml_file in xml_files:
        try:
            file_name = xml_file['file_name']
            content = xml_file['content']
            full_file_path = os.path.join(project_path, target_file_path, file_name)

            # 替换或创建文件
            replace_or_create_file(full_file_path, content)

            # 运行Lint检查
            lint(full_file_path)
        except Exception as e:
            print(f"Error processing file {xml_file['file_name']}: {e}")

def process_ets_files(ets_files, project_path, target_file_path):
    """
    批量处理ETS文件：替换模板项目中的文件内容并运行Lint检查。

    :param ets_files: 包含ETS代码的列表，每个元素是一个字典，格式为 {'file_name': '文件名', 'content': 'ETS内容'}
    :param project_path: 模板项目的路径
    :param target_file_path: 模板项目中目标文件的相对路径
    """
    for ets_file in ets_files:
        try:
            file_name = ets_file['file_name']
            content = ets_file['content']
            full_file_path = os.path.join(project_path, target_file_path, file_name)

            # 替换或创建文件
            replace_or_create_file(full_file_path, content)

            # 运行Lint检查
            lint(full_file_path)
        except Exception as e:
            print(f"Error processing file {ets_file['file_name']}: {e}")


# 示例调用
if __name__ == "__main__":
    # 模板项目路径
    project_path = "C:/Users/74187/AndroidStudioProjects/MinApplication"
    target_file_path = "app/src/main/res/layout"

    # 示例XML文件列表
    xml_files = [
        {'file_name': 'activity_main.xml', 'content': '<LinearLayout></LinearLayout>'},
        {'file_name': 'activity_second.xml', 'content': '<RelativeLayout></RelativeLayout>'}
    ]

    process_xml_files(xml_files, project_path, target_file_path)
# if __name__ == "__main__":
