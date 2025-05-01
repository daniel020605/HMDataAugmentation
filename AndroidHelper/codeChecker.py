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


# if __name__ == "__main__":
