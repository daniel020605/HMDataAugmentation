import os

from torch.fx.experimental.unification import variables

BUILD_TEMPLATE = """
{imports}

@Entry
@Component
struct {file_name} {{
  {variables}
  {build}
  {solution}
}}
"""

FUNC_TEMPLATE = """
{imports}

struct {file_name} {{
  {variables}
  {solution}
}}
"""
def get_ui_code(data, file_name="Index"):
    imports = []
    xl_context = []
    for imp in data.get('import', []):
        if imp['module_name'].startswith('.'):
            xl_context.append(imp["component_content"])
        else:
            imports.append(imp['full_import'])
    variables = [v['full_variable'] for v in data.get('variables', [])]
    solution = data.get('content', '')
    return xl_context, BUILD_TEMPLATE.format(
                        file_name=file_name,
                        imports="\n".join(imports),
                        variables="\n".join(v for v in variables),
                        build=solution)

def get_fx_code(data, file_name="Index"):
    imports = []
    xl_context = []
    for imp in data.get('import', []):
        if imp['module_name'].startswith('.'):
            xl_context.append(imp["component_content"])
        else:
            imports.append(imp['full_import'])
    variables = [v['full_variable'] for v in data.get('variables', [])]
    solution = data.get('content', '')
    return xl_context, FUNC_TEMPLATE.format(
                        file_name=file_name,
                        imports="\n".join(imports),
                        variables="\n".join(v for v in variables),
                        solution=solution)


# if __name__ == "__main__":