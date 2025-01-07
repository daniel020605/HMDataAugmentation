import os
import subprocess

def run_command(command, cwd=None):
    """
    运行命令行工具命令并打印输出
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        print("Command Output:\n", result.stdout)
        if result.stderr:
            print("Command Errors:\n", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error while executing command: {e}")
        return False

def check_and_build_android_project(project_path):
    """
    对指定路径下的 Android 项目进行代码检查和编译
    """
    if not os.path.exists(project_path):
        print(f"Error: Path {project_path} does not exist.")
        return False

    # Step 1: Run lint to check the code
    print("Running lint...")
    lint_command = "./gradlew lint"
    lint_success = run_command(lint_command, cwd=project_path)
    if not lint_success:
        print("Lint failed. Please fix the issues and try again.")
        return False

    # Step 2: Build the project
    print("Building the project...")
    build_command = "./gradlew build"
    build_success = run_command(build_command, cwd=project_path)
    if not build_success:
        print("Build failed. Please check the errors and try again.")
        return False

    print("Lint and build completed successfully!")
    return True

if __name__ == "__main__":
    # 指定 Android 项目的路径
    project_path = "/Users/daniel/Desktop/Android/Android"
    check_and_build_android_project(project_path)