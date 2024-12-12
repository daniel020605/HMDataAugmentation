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


if __name__ == '__main__':
    sft2corpus("./docs/datas/records.json")