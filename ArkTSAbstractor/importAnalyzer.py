import re

class ETSFileReferences:
    def __init__(self, file_path):
        self.file_path = file_path
        self.references = []

    def add_reference(self, import_type, module_name, full_import, component_name=None, alias=None):
        reference = {
            'import_type': import_type,
            'module_name': module_name,
            'full_import': full_import,
            'component_name': component_name,
            'alias': alias
        }
        self.references.append(reference)

def analyze_imports(file_content):
    references = ETSFileReferences(file_content)
    import_pattern = re.compile(r'import\s+([^;]+)\s+from\s+["\']([^"\']+)["\'];')
    side_effect_pattern = re.compile(r'import\s+["\']([^"\']+)["\'];')

    for line in file_content.splitlines():
        match = import_pattern.match(line)
        if match:
            full_import = match.group(0).replace('{', '{').replace('}', '}')
            imports, module_name = match.groups()
            if imports.startswith('{'):
                named_imports = [imp.strip() for imp in imports[1:-1].split(',')]
                for imp in named_imports:
                    if ' as ' in imp:
                        component_name, alias = imp.split(' as ')
                        references.add_reference('named', module_name, full_import, component_name.strip(), alias.strip())
                    else:
                        references.add_reference('named', module_name, full_import, imp.strip())
            elif imports.startswith('* as'):
                alias = imports.split(' as ')[1].strip()
                references.add_reference('namespace', module_name, full_import, alias=alias)
            else:
                if ' as ' in imports:
                    component_name, alias = imports.split(' as ')
                    references.add_reference('default', module_name, full_import, component_name.strip(), alias.strip())
                else:
                    references.add_reference('default', module_name, full_import, component_name=imports.strip())
        elif side_effect_pattern.match(line):
            module_name = side_effect_pattern.match(line).group(1)
            references.add_reference('side_effect', full_import, module_name)

    return references
