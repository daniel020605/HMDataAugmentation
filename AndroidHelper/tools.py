import os

def check_files_in_functions_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if len(content) < 30:
                    print(f"File: {filename}")
                    print(content)
                    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    functions_folder = './functions'
    check_files_in_functions_folder(functions_folder)