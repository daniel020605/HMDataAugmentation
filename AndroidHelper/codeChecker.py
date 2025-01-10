import os
import subprocess

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

def check_and_build_android_project(project_path):
    """
    对指定路径下的 Android 项目进行代码检查和编译
    """
    if not os.path.exists(project_path):
        print(f"Error: Path {project_path} does not exist.")
        return False

    chmod_command = f"chmod +x {project_path}/gradlew"
    chmod_success = run_command(chmod_command)
    if not chmod_success:
        print("Error while changing gradlew permissions.")
        return False

    # Step 1: Sync project with Gradle files
    print("Syncing project with Gradle files...")
    sync_command = "./gradlew --refresh-dependencies"
    sync_success = run_command(sync_command, cwd=project_path)
    if not sync_success:
        print("Sync failed. Please check the errors and try again.")
        return False

    # Step 2: Run lint to check the code
    print("Running lint...")
    lint_command = "./gradlew lint"
    lint_success = run_command(lint_command, cwd=project_path)
    if not lint_success:
        print("Lint failed. Please fix the issues and try again.")
        return False

    # Step 3: Build the project
    print("Building the project...")
    build_command = "./gradlew build"
    build_success = run_command(build_command, cwd=project_path)
    if not build_success:
        print("Build failed. Please check the errors and try again.")
        return False

    print("Sync, lint, and build completed successfully!")
    return True

if __name__ == "__main__":
    # 指定 Android 项目的路径
    project_path = "/Users/daniel/Desktop/Android/chatgpt-android"
    check_and_build_android_project(project_path)