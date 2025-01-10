from codeChecker import check_and_build_android_project
from projectPreprocessor import gradle_source_replace

if __name__ == '__main__':
    project_path = "/Users/daniel/Desktop/Android/chatgpt-android"

    gradle_source_replace(project_path)
    check_and_build_android_project(project_path)