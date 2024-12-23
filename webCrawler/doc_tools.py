import os


# 替换文档中的换行符
def change_line(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content.replace('\\n', '\n'))
            except UnicodeDecodeError:
                print(f"Skipping file due to encoding error: {file_path}")


# "harmonyos-guides-V5" "harmonyos-guides-V5" "best-practices-V5"
if __name__ == '__main__':
    change_line("best-practices-V5")