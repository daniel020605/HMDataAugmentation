import re

def gradle_source_replace(project_path):
    # 文件路径
    file_path = project_path + '/gradle/wrapper/gradle-wrapper.properties'

    # 读取文件内容
    with open(file_path, 'r') as file:
        content = file.read()

    # 替换distributionUrl属性
    # new_content = re.sub(
    #     r'distributionUrl=https\\://services.gradle.org/distributions/gradle-(.*?)-bin.zip',
    #     r'distributionUrl=https\://mirrors.cloud.tencent.com/gradle/gradle-\1-bin.zip',
    #     content
    # )

    #将"services.gradle.org/distributions"替换为"mirrors.cloud.tencent.com/gradle"
    new_content = re.sub(
        r'services.gradle.org/distributions',
        r'mirrors.cloud.tencent.com/gradle',
        content
    )

    # 保存文件
    with open(file_path, 'w') as file:
        file.write(new_content)

if __name__ == '__main__':
    project_path = "/Users/daniel/Desktop/Android/FakeBiliBili"
    gradle_source_replace(project_path)