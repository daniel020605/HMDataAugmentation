from AndroidHelper.projectAnalyser import extract_functions_from_project, save_functions_to_json
from codeChecker import check_and_build_android_project
from projectPreprocessor import gradle_source_replace

if __name__ == '__main__':
    project_name = "android-final"
    project_path = "/Users/daniel/Desktop/Android/" + project_name
    output_path = f"./functions/{project_name}.json"

    gradle_source_replace(project_path)
    check_and_build_android_project(project_path)
    functions_dict = extract_functions_from_project(project_path)
    save_functions_to_json(functions_dict, output_path)