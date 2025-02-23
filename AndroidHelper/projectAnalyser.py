import os
import re
import json
from tqdm import tqdm

def extract_functions_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Simplified regular expression to match Java/Kotlin function definitions
        function_pattern = re.compile(r'(public|protected|private|static|\s)*[\w<>\[\]]+\s+\w+\s*\([^\)]*\)\s*\{', re.DOTALL)
        functions = []
        brace_count = 0
        function_start = None

        for match in function_pattern.finditer(content):
            if function_start is None:
                function_start = match.start()
            brace_count += 1

            for i in range(match.end(), len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        functions.append(content[function_start:i+1])
                        function_start = None
                        break

        return functions
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return []

def extract_functions_from_project(project_path):
    functions_dict = {}

    for root, _, files in os.walk(project_path):
        for file in tqdm(files):
            if file.endswith('.java') or file.endswith('.kt'):
                file_path = os.path.join(root, file)
                functions = extract_functions_from_file(file_path)
                if functions:
                    functions_dict[file_path] = functions

    return functions_dict

def save_functions_to_json(functions_dict, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(functions_dict, json_file, indent=4)
    except Exception as e:
        print(f"Error saving to JSON file {output_path}: {e}")

if __name__ == "__main__":
    project_path = "/Users/daniel/Desktop/Android/Android"
    output_path = "./functions/Android.json"

    functions_dict = extract_functions_from_project(project_path)
    save_functions_to_json(functions_dict, output_path)