import json
import os
from bs4 import BeautifulSoup
import re

def process_file(file_path):
    
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    # 根据文件内容调用相应的处理函数
    if soup.find('div', {'id': '\\"成员变量\\"'}):
        extract_class_info(soup)
    if soup.find('div', {'id': '\\"枚举\\"'}):
        find_enum_section(soup)
    if soup.find('div', {'id': '\\"枚举类型说明\\"'}):
        find_enum_section2(soup)
    if soup.find('div', {'id': '\\"函数说明\\"'}):
        find_functions_section(soup)
    if soup.find('div', {'id': '\\"成员变量\\"'}):
        extract_class_info(soup)
    if soup.find('div', {'id': '\\"类型定义\\"'}):
        extract_type_definitions(soup)


def find_enum_section(soup):
# 定位到 id 为 "枚举" 的 div 标签
    enum_section = soup.find('div', {'id': '\\"枚举\\"'})
    res = ""

    if enum_section:
        # 提取枚举数据
        enum_data = []
        for row in enum_section.find_all('tr')[1:]:  # 跳过表头
            name_cell, desc_cell = row.find_all('td')
            enum_name = name_cell.find('a').text.strip()
            description = desc_cell.text.strip()
            enum_values = re.findall(r'(\w+)\s*=\s*(\d+)', name_cell.text)
            for value_name, value in enum_values:
                enum_data.append((enum_name, value_name, value, description))

        # 生成插入语句
        for enum_name, value_name, value, description in enum_data:
            res.append(f"INSERT INTO HMEnums (EnumName, SystemCapability, EnumValueName, EnumValue, Description) VALUES ('{enum_name}', 'SystemCapability.Communication.Bluetooth.Core', '{value_name}', '{value}', '{description}');\n")
        return res
    else:
        print("未找到 id 为 '枚举' 的 div 标签")

def find_enum_section2(soup):
    # 定位到 id 为 "枚举类型说明" 的 div 标签
    enum_type_section = soup.find('div', {'id': '\\"枚举类型说明\\"'})
    res = ""

    if enum_type_section:
        # 找到下一个 div 标签
        next_div = enum_type_section.find_next('div')
        
        if next_div:
            # 提取枚举数据
            enum_name = next_div.find('h4').text.strip().replace('[h2]', '')
            description = next_div.find('p', text='定义签名验签参数类型。').text.strip()
            enum_data = []
            
            for row in next_div.find_all('tr')[1:]:  # 跳过表头
                value_name, value_desc = row.find_all('td')
                value_name = value_name.text.strip()
                value_desc = value_desc.text.strip()
                enum_data.append((enum_name, value_name, value_desc, description))
            
            # 生成插入语句
            for enum_name, value_name, value_desc, description in enum_data:
                res.append(f"INSERT INTO HMEnums (EnumName, SystemCapability, EnumValueName, EnumValue, Description) VALUES ('{enum_name}', 'SystemCapability.Communication.Bluetooth.Core', '{value_name}', NULL, '{value_desc}');")
        else:
            print("未找到下一个 div 标签")
        return res
    else:
        print("未找到 id 为 '枚举类型说明' 的 div 标签")


def find_functions_section(soup):
    # 定位到 id 为 "函数说明" 的 div 标签
    function_section = soup.find('div', {'id': '\\"函数说明\\"'})
    res = ""
    
    if function_section:
        # 找到接下来的所有 div 标签
        next_divs = function_section.find_all_next('div', class_='\\"section\\"')
        
        for next_div in next_divs:
            try:
                function_name = next_div.find('h4').text.strip().replace('[h2]', '')
                function_signature = next_div.find('pre', class_='\\"screen\\"').text.strip()
                description = next_div.find('p', string='描述').find_next_sibling('p').text.strip()
                # version = next_div.find('p', string='起始版本：').find_next_sibling('p').text.strip()
                
                # 提取返回类型
            # 提取返回类型
                return_type_match = re.match(r'^(const\s+)?(\w+\s*\*?)', function_signature)
                return_type = return_type_match.group(2) if return_type_match else ''
                
      
                # 提取参数
                parameters = []
                param_section = next_div.find('p', string='参数:').find_next_sibling('div', class_='\\"tablenoborder\\"')
                if param_section:
                    for row in param_section.find_all('tr')[1:]:  # 跳过表头
                        param_name, param_desc = row.find_all('td')
                        param_name = param_name.text.strip()
                        param_desc = param_desc.text.strip()
                        param_type = re.search(r'\b(\w+)\b', param_desc).group(1) if re.search(r'\b(\w+)\b', param_desc) else ''
                        parameters.append({
                            "param_name": param_name,
                            "param_type": param_type,
                            "required": "true"
                        })
   
                # 将参数列表转换为 JSON 字符串
                parameters_json = json.dumps(parameters, ensure_ascii=False)
               
        
                # 提取返回值
                return_values = []
                return_section = next_div.find('p', string='返回：').find_next_sibling('p')
                while return_section and return_section.name == 'p':
                    return_value = return_section.text.strip()
                    if ' - ' in return_value:
                        value, info = return_value.split(' - ', 1)
                        return_values.append({
                            "value": value.strip(),
                            "info": info.strip()
                        })
                    return_section = return_section.find_next_sibling('p')
                
                # 将返回值列表转换为 JSON 字符串
                return_values_json = json.dumps(return_values, ensure_ascii=False)
                
                 # 提取错误码
                error_codes = []
                error_section = next_div.find('p', string='返回：').find_next_sibling('p')
                while error_section and error_section.name == 'p':
                    error_code = error_section.text.strip()
                    if ' - ' in error_code:
                        value, info = error_code.split(' - ', 1)
                        error_codes.append({
                            "value": value.strip(),
                            "info": info.strip()
                        })
                    error_section = error_section.find_next_sibling('p')
                
                # 将错误码列表转换为 JSON 字符串
                error_codes_json = json.dumps(error_codes, ensure_ascii=False)
                
                # 生成插入语句
                res.append(f"INSERT INTO HMFunctions (FunctionName, FunctionParameters, ReturnType, ReturnValue, FullFunctionName, RequiredPermissions, SystemCapability, ErrorCodes, Example, FunctionDescription) VALUES ('{function_name}', '{str(parameters_json)}', '{return_type}', '{return_values_json}', '{function_signature}', '-', 'SystemCapability.Communication.Bluetooth.Core', '{error_codes_json}', NULL, '{description}');")
            except AttributeError:
                # 跳过不包含函数内容的 div 标签
                continue
        return res
    else:
        print("未找到 id 为 '函数说明' 的 div 标签")


def extract_class_info(soup):
    # 获取类名
    class_name = soup.find('h1').text.strip()

    # 提取成员变量
    member_variables = []
    member_section = soup.find('div', {'id': '\\"成员变量\\"'})
    if member_section:
        rows = member_section.find_all('tr')[1:]  # 跳过表头
        for row in rows:
            name_cell, desc_cell = row.find_all('td')
            member_name = name_cell.text.strip()
            member_desc = desc_cell.text.strip()
            member_variables.append({
                "name": member_name,
                "description": member_desc
            })

        # 将成员变量列表转换为 JSON 字符串
        member_variables_json = json.dumps(member_variables, ensure_ascii=False)

        # 提取类描述
        class_description = soup.find('div', {'id': '\\"概述\\"'}).find('p').text.strip()

        # 生成插入语句
        sql = f"""
        INSERT INTO HMClasses (
            ClassName, MemberVariables, Methods, Constructors, InnerClasses, Example, ClassDescription
        ) VALUES (
            '{class_name}', '{member_variables_json}', NULL, NULL, NULL, NULL, '{class_description}'
        );
        """
        return sql

def extract_type_definitions(soup):
    # 定位到 id 为 "类型定义" 的 div 标签
    type_def_section = soup.find('div', {'id': '\\"类型定义\\"'})

    if type_def_section:
        # 提取类型定义数据
        type_definitions = []
        rows = type_def_section.find_all('tr')[1:]  # 跳过表头
        for row in rows:
            name_cell, desc_cell = row.find_all('td')
            type_name = name_cell.text.strip()
            description = desc_cell.text.strip()

            # 判断类型类别
            if 'typedef struct' in type_name:
                type_category = 'struct'
            elif 'typedef enum' in type_name:
                type_category = 'enum'
            elif 'typedef void(*' in type_name:
                type_category = 'function pointer'
            else:
                type_category = 'unknown'

            type_definitions.append({
                "TypeName": type_name,
                "TypeCategory": type_category,
                "Description": description
            })

        # 生成插入语句
        for type_def in type_definitions:
                    sql = f"INSERT INTO HMTypeDefinitions (TypeName, TypeCategory, Description) VALUES ('{type_def['TypeName']}', '{type_def['TypeCategory']}', '{type_def['Description']}');"
                    return sql
    else:
        print("未找到 id 为 '类型定义' 的 div 标签")

def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                process_file(file_path)

# with open('/Users/daniel/Desktop/Projects/HMDataAugmentation/webCrawler/harmonyos-references-V5/dataguard-V5.html', 'r', encoding='utf-8') as file:
#     html_content = file.read()

# soup = BeautifulSoup(html_content, 'html.parser')

# extract_class_info(soup)
# find_enum_section(soup)
# find_enum_section2(soup)
# find_functions_section(soup)

path = '/Users/daniel/Desktop/Projects/HMDataAugmentation/webCrawler/harmonyos-references-V5'
process_folder(path)