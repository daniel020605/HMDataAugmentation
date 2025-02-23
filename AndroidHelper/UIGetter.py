import json
import os
import re
import shutil


def find_xml_files(project_path):
    xml_files = []
    layout_path = os.path.join(project_path, 'app/src/main/res/layout')
    if os.path.exists(layout_path):
        for root, _, files in os.walk(layout_path):
            for file in files:
                if file.endswith('.xml'):
                    xml_files.append(os.path.join(root, file))
    return xml_files


def copy_xml_files(project_name, xml_files, destination_path):
    project_ui_path = os.path.join(destination_path, project_name)
    os.makedirs(project_ui_path, exist_ok=True)

    for xml_file in xml_files:
        shutil.copy(xml_file, project_ui_path)


def extract_composable_functions(project_path):
    composable_functions = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.kt'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    functions = re.findall(r'(@Composable\s+fun\s+\w+\s*\(.*?\)\s*{.*?})', content, re.DOTALL)
                    for function in functions:
                        if '@Preview' not in function:
                            composable_functions.append('@Preview\n' + function)
    return composable_functions


def save_composable_functions_as_json(project_name, composable_functions, destination_path):
    project_ui_path = os.path.join(destination_path, project_name)
    os.makedirs(project_ui_path, exist_ok=True)

    json_path = os.path.join(project_ui_path, 'composable_functions.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(composable_functions, f, indent=4)


def get_UI(project_path, destination_path):

    project_name = os.path.basename(project_path.strip('/'))

    find_xml_files(project_path)
    copy_xml_files(project_name, find_xml_files(project_path), destination_path)
    print(f"xml files saved to {os.path.join(destination_path, project_name)}")

    composable_functions = extract_composable_functions(project_path)
    save_composable_functions_as_json(project_name, composable_functions, destination_path)

    print(f"Composable functions saved to {os.path.join(destination_path, project_name)}")


if __name__ == "__main__":
    project_name = "QMUI_Android"
    project_path = "/Users/daniel/Desktop/Android/" + project_name
    UI_path = "./UI/"
    get_UI(project_path, UI_path)