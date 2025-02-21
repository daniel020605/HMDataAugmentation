import json
import os
from bs4 import BeautifulSoup
import re

from tqdm import tqdm


def is_file_processed(file_path, output_folder):
    output_file_path = os.path.join(output_folder, os.path.basename(file_path).replace('.html', '.sql'))
    return os.path.exists(output_file_path)

def process_file(file_path, output_folder):
    if is_file_processed(file_path, output_folder):
        print(f"Skipping already processed file: {file_path}")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    sql_statements = ""

    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    if os.path.basename(file_path).startswith("errorcode"):
        sql_statements += extract_error_code_info(soup)
    if soup.find('div', {'id': '\\"成员变量\\"'}):
        sql_statements += (extract_class_info(soup))
    if soup.find('div', {'id': '\\"枚举\\"'}):
        sql_statements += (find_enum_section(soup))
    if soup.find('div', {'id': '\\"枚举类型说明\\"'}):
        sql_statements += (find_enum_section2(soup))
    if soup.find('div', {'id': '\\"函数说明\\"'}):
        sql_statements += (find_functions_section(soup))
    if soup.find('div', {'id': '\\"成员变量\\"'}):
        sql_statements += (extract_class_info(soup))
    if soup.find('div', {'id': '\\"类型定义\\"'}):
        sql_statements += (extract_type_definitions(soup))
    if soup.find('div', {'id': '\\"pub-attribs\\"'}):
        sql_statements += (extract_struct_info(soup))
    if soup.find('div', {'id': '\\"接口\\"'}):
        sql_statements += ((soup))
    output_file_path = os.path.join(output_folder, os.path.basename(file_path).replace('.html', '.sql'))
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(sql_statements + '\n')


def extract_error_code_info(soup):
    error_codes = []

    sections = soup.find_all('div', class_='\\"section\\"')
    for section in sections:
        error_code = section.find('h4').text.strip()
        error_info_tag = section.find('p', string='错误信息')
        error_info = error_info_tag.find_next_sibling('p').text.strip() if error_info_tag and error_info_tag.find_next_sibling('p') else ''
        error_description_tag = section.find('p', string='错误描述')
        error_description = error_description_tag.find_next_sibling('p').text.strip() if error_description_tag and error_description_tag.find_next_sibling('p') else ''
        possible_causes_tag = section.find('p', string='可能原因')
        possible_causes = [li.text.strip() for li in possible_causes_tag.find_next_sibling('ol').find_all('li')] if possible_causes_tag and possible_causes_tag.find_next_sibling('ol') else []
        handling_steps_tag = section.find('p', string='处理步骤')
        handling_steps = [li.text.strip() for li in handling_steps_tag.find_next_sibling('ol').find_all('li')] if handling_steps_tag and handling_steps_tag.find_next_sibling('ol') else []

        error_codes.append({
            "error_code": error_code,
            "error_info": error_info,
            "error_description": error_description,
            "possible_causes": possible_causes,
            "handling_steps": handling_steps
        })

    sql_statements = ""
    for error in error_codes:
        sql_statements += f"INSERT INTO ErrorCodes (ErrorCode, ErrorInfo, ErrorDescription, PossibleCauses, HandlingSteps) VALUES ('{error['error_code']}', '{error['error_info']}', '{error['error_description']}', '{json.dumps(error['possible_causes'], ensure_ascii=False)}', '{json.dumps(error['handling_steps'], ensure_ascii=False)}');\n"

    return sql_statements



def find_enum_section(soup):
    enum_section = soup.find('div', {'id': '\\"枚举\\"'})
    res = ""

    system_capability = ''
    api_level = ''

    overview_section = soup.find('div', {'id': '\\"概述\\"'})
    if overview_section:
        # Extract system capability
        system_capability_tag = overview_section.find('p', string=re.compile(r'系统能力：'))
        if system_capability_tag:
            system_capability = system_capability_tag.text.split('：')[-1].strip()

        # Extract API level
        api_level_tag = overview_section.find('p', string=re.compile(r'起始版本：'))
        if api_level_tag:
            api_level = api_level_tag.text.split('：')[-1].strip()

    if enum_section:
        enum_data = []
        for row in enum_section.find_all('tr')[1:]:
            name_cell, desc_cell = row.find_all('td')
            name_anchor = name_cell.find('a')
            if name_anchor:
                enum_name = name_anchor.text.strip()
                description = desc_cell.text.strip()
                enum_values = re.findall(r'(\w+)\s*=\s*(\d+)', name_cell.text)
                for value_name, value in enum_values:
                    enum_data.append((enum_name, value_name, value, description+api_level))

        for enum_name, value_name, value, description in enum_data:
            res += f"INSERT INTO HMEnums (EnumName, SystemCapability, EnumValueName, EnumValue, Description) VALUES ('{enum_name}', '{system_capability}', '{value_name}', '{value}', '{description}');\n"
        return res
    else:
        print("未找到 id 为 '枚举' 的 div 标签")
        return ''


def find_enum_section2(soup):
    enum_type_section = soup.find('div', {'id': '\\"枚举类型说明\\"'})
    res = ""

    system_capability = ''
    api_level = ''

    overview_section = soup.find('div', {'id': '\\"概述\\"'})
    if overview_section:
        # Extract system capability
        system_capability_tag = overview_section.find('p', string=re.compile(r'系统能力：'))
        if system_capability_tag:
            system_capability = system_capability_tag.text.split('：')[-1].strip()

        # Extract API level
        api_level_tag = overview_section.find('p', string=re.compile(r'起始版本：'))
        if api_level_tag:
            api_level = api_level_tag.text.split('：')[-1].strip()

    if enum_type_section:
        next_div = enum_type_section.find_next('div')

        if next_div:
            enum_name = next_div.find('h4').text.strip().replace('[h2]', '')
            description_tag = next_div.find('p', string='定义签名验签参数类型。')
            description = description_tag.text.strip() if description_tag else ''
            enum_data = []

            for row in next_div.find_all('tr')[1:]:
                value_name, value_desc = row.find_all('td')
                value_name = value_name.text.strip()
                value_desc = value_desc.text.strip()
                enum_data.append((enum_name, value_name, value_desc, description + api_level))

            for enum_name, value_name, value_desc, description in enum_data:
                res += f"INSERT INTO HMEnums (EnumName, SystemCapability, EnumValueName, EnumValue, Description) VALUES ('{enum_name}', '{system_capability}', '{value_name}', NULL, '{value_desc}');\n"
        else:
            print("未找到下一个 div 标签")
        return res
    else:
        print("未找到 id 为 '枚举类型说明' 的 div 标签")
        return ''


def find_functions_section(soup):
    function_section = soup.find('div', {'id': '\\"函数说明\\"'})
    res = ""

    system_capability = ''
    api_level = ''

    overview_section = soup.find('div', {'id': '\\"概述\\"'})
    if overview_section:
        # Extract system capability
        system_capability_tag = overview_section.find('p', string=re.compile(r'系统能力：'))
        if system_capability_tag:
            system_capability = system_capability_tag.text.split('：')[-1].strip()

        # Extract API level
        api_level_tag = overview_section.find('p', string=re.compile(r'起始版本：'))
        if api_level_tag:
            api_level = api_level_tag.text.split('：')[-1].strip()

    if function_section:
        next_divs = function_section.find_all_next('div', class_='\\"section\\"')

        for next_div in next_divs:
            function_name_tag = next_div.find('h4')
            function_signature_tag = next_div.find('pre', class_='\\"screen\\"')
            description_tag = next_div.find('p', string='描述')

            if function_name_tag and function_signature_tag:
                function_name = function_name_tag.text.strip().replace('[h2]', '')
                function_signature = function_signature_tag.text.strip()
                description = description_tag.find_next_sibling('p').text.strip() if description_tag else ''

                return_type_match = re.match(r'^(const\s+)?(\w+\s*\*?)', function_signature)
                return_type = return_type_match.group(2) if return_type_match else ''

                parameters = []
                param_section_tag = next_div.find('p', string='参数:')
                if param_section_tag:
                    param_section = param_section_tag.find_next_sibling('div', class_='\\"tablenoborder\\"')
                    if param_section:
                        for row in param_section.find_all('tr')[1:]:
                            param_name, param_desc = row.find_all('td')
                            param_name = param_name.text.strip()
                            param_desc = param_desc.text.strip()
                            param_type = re.search(r'\b(\w+)\b', param_desc).group(1) if re.search(r'\b(\w+)\b', param_desc) else ''
                            parameters.append({
                                "param_name": param_name,
                                "param_type": param_type,
                                "required": "true"
                            })

                parameters_json = json.dumps(parameters, ensure_ascii=False)

                return_values = []
                return_section = next_div.find('p', string='返回：')
                if return_section:
                    return_section = return_section.find_next_sibling('p')
                    while return_section and return_section.name == 'p':
                        return_value = return_section.text.strip()
                        if ' - ' in return_value:
                            value, info = return_value.split(' - ', 1)
                            return_values.append({
                                "value": value.strip(),
                                "info": info.strip()
                            })
                        return_section = return_section.find_next_sibling('p')

                return_values_json = json.dumps(return_values, ensure_ascii=False)

                error_codes = []
                error_section = next_div.find('p', string='返回：')
                if error_section:
                    error_section = error_section.find_next_sibling('p')
                    while error_section and error_section.name == 'p':
                        error_code = error_section.text.strip()
                        if ' - ' in error_code:
                            value, info = error_code.split(' - ', 1)
                            error_codes.append({
                                "value": value.strip(),
                                "info": info.strip()
                            })
                        error_section = error_section.find_next_sibling('p')

                error_codes_json = json.dumps(error_codes, ensure_ascii=False)

                res += (f"INSERT INTO HMFunctions (FunctionName, FunctionParameters, ReturnType, ReturnValue, FullFunctionName, RequiredPermissions, SystemCapability, ErrorCodes, Example, FunctionDescription) VALUES ('{function_name}', '{str(parameters_json)}', '{return_type}', '{return_values_json}', '{function_signature}', '-', '{system_capability}', '{error_codes_json}', NULL, '{description}');\n")
        return res
    else:
        print("未找到 id 为 '函数说明' 的 div 标签")
        return ''


def extract_class_info(soup):
    # 获取类名
    class_name = soup.find('h1').text.strip()

    # 提取成员变量
    member_variables = []
    member_section = soup.find('div', {'id': '\\"成员变量\\"'})

    if member_section:
        rows = member_section.find_all('tr')[1:]  # 跳过表头
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                name_cell, desc_cell = cells
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



def extract_struct_info(soup):
    struct_section = soup.find('div', {'id': '\\"pub-attribs\\"'})
    res = ""

    if struct_section:
        # Extract class name
        class_name = soup.find('h1').text.strip()

        # Extract member variables
        member_variables = []
        rows = struct_section.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                name_cell, desc_cell = cells
                member_type = name_cell.text.strip().split('\n')[0]
                member_name = name_cell.text.strip().split('\n')[-1]
                member_desc = desc_cell.text.strip()
                member_variables.append({
                    "type": member_type,
                    "name": member_name,
                    "description": member_desc
                })

        # Convert member variables list to JSON string
        member_variables_json = json.dumps(member_variables, ensure_ascii=False)

        # Generate SQL insert statement
        sql = f"""
        INSERT INTO HMStructs (
            StructName, MemberVariables
        ) VALUES (
            '{class_name}', '{member_variables_json}'
        );
        """
        return sql
    else:
        print("未找到 id 为 'pub-attribs' 的 div 标签")
        return ''

def extract_type_definitions(soup):
    # 定位到 id 为 "类型定义" 的 div 标签
    type_def_section = soup.find('div', {'id': '\\"类型定义\\"'})
    res = ""
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
            res += sql + '\n'
        return res
    else:
        print("未找到 id 为 '类型定义' 的 div 标签")


def process_folder(folder_path, output_folder):
    for root, dirs, files in os.walk(folder_path):
        for file in tqdm(files):
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                process_file(file_path, output_folder)

# with open('/Users/daniel/Desktop/Projects/HMDataAugmentation/webCrawler/harmonyos-references-V5/dataguard-V5.html', 'r', encoding='utf-8') as file:
#     html_content = file.read()

# soup = BeautifulSoup(html_content, 'html.parser')

# extract_class_info(soup)
# find_enum_section(soup)
# find_enum_section2(soup)
# find_functions_section(soup)
if __name__ == '__main__':
    path = './harmonyos-references-V5'
    output_folder = './harmony-references-V5-sql'
    process_folder(path, output_folder)