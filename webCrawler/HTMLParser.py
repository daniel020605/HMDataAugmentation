import os
from bs4 import BeautifulSoup

def html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    article = soup.find('article')
    if article:
        text = article.get_text()
        # 清除空行和[NBSP]
        text = text.replace('\xa0', ' ').strip()
        text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
        return text
    else:
        return ''

def save_text_to_file(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def process_html_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for root, _, files in os.walk(input_dir):
        for file in files:
            input_file_path = os.path.join(root, file)
            output_file_path = os.path.join(output_dir, file + '.txt')

            with open(input_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            text_content = html_to_text(html_content)
            save_text_to_file(text_content, output_file_path)
            print(f"Processed {input_file_path} -> {output_file_path}")


if __name__ == "__main__":
    input_directory = './test'
    output_directory = './output'
    process_html_files(input_directory, output_directory)