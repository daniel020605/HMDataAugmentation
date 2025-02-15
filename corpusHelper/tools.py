import os
# 将字符串中所有\n转换成换行
def replace_all_newline(string):
    return string.replace("\\n", "\n")


import json

def sft2corpus(sft):
    with open(sft, "r", encoding="utf-8") as f:
        data = json.load(f)
        corpus = []
        for item in data:
            corpus.append({'content': item["context"] + item["question"] + item["answer"]})
    with open(sft, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=4)

def rename_txt_to_html(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                old_file_path = os.path.join(root, file)
                new_file_path = os.path.join(root, file.replace('.txt', '.html'))
                os.rename(old_file_path, new_file_path)

if __name__ == '__main__':
    # sft2corpus("./docs/datas/records.json")
    rename_txt_to_html("./harmonyos-references-V5")