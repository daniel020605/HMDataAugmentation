import os
import re

def sloveFile(filepath, initial_file, original_name, alias_name):
    initial_dir = os.path.dirname(os.path.abspath(initial_file))
    absolute_filepath = os.path.join(initial_dir, filepath + '.ets')

    with open(absolute_filepath, 'r', encoding='utf-8') as file:
        content = file.readlines()

    line_index = -1
    pattern = re.compile(rf'\b{re.escape(original_name)}\b')
    for i, line in enumerate(content):
        if pattern.search(line):
            line_index = i
            break

    if line_index == -1:
        print(f"Original name '{original_name}' not found in the file.")
        return

    start_index = line_index
    while start_index > 0 and content[start_index].strip().startswith('@'):
        start_index -= 1

    first_char = None
    for char in content[line_index]:
        if char in '{[':
            first_char = char
            break

    if not first_char:
        print("No opening brace found after the original name.")
        return

    if first_char == '{':
        open_brace, close_brace = '{', '}'
    else:
        open_brace, close_brace = '[', ']'

    brace_count = 0
    start_brace_found = False
    end_index = line_index

    while end_index < len(content):
        brace_count += content[end_index].count(open_brace)
        brace_count -= content[end_index].count(close_brace)
        if open_brace in content[end_index]:
            start_brace_found = True
        if start_brace_found and brace_count == 0:
            break
        end_index += 1

    matched_content = ''.join(content[start_index:end_index + 1])
    replaced_content = matched_content.replace(original_name, alias_name)
    print(replaced_content)

    return replaced_content

def remove_comments(content):
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    return content

def split_import_statement(statement):
    pattern = re.compile(r'import\s*\{\s*(.*?)\s*\}\s*from\s*[\'"](.*?)[\'"];')
    match = pattern.match(statement)
    if match:
        imports, path = match.groups()
        imports_list = imports.split(',')
        result = []
        for imp in imports_list:
            imp = imp.strip()
            if ' as ' in imp:
                original, alias = imp.split(' as ')
                result.append((original.strip(), alias.strip()))
            else:
                result.append((imp, imp))
        return result, path
    return None

def parse_import_statements(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    content = remove_comments(content)
    import_statements = re.findall(r'import\s*\{.*?\}\s*from\s*[\'"].*?[\'"];', content)
    parsed_imports = []
    for statement in import_statements:
        parsed_import = split_import_statement(statement)
        if parsed_import:
            parsed_imports.append(parsed_import)
            content = content.replace(statement, '')
    return parsed_imports, content, import_statements

if __name__ == '__main__':
    filepath = '/Users/rain/Downloads/OxHornCampus/entry/src/main/ets/pages/MainPage.ets'
    new_filepath = './NewMainPage.ets'
    parsed_imports, initial_content, import_statements = parse_import_statements(filepath)

    with open(new_filepath, 'w', encoding='utf-8') as new_file:
        for imports, path in parsed_imports:
            if path.startswith('@'):
                new_file.write(f'import {{ {", ".join([alias for _, alias in imports])} }} from "{path}";\n')

        new_file.write(initial_content)

        for imports, path in parsed_imports:
            if not path.startswith('@'):
                for original, alias in imports:
                    content = sloveFile(path, filepath, original, alias)
                    new_file.write('\n' + content)
                    print('----------')