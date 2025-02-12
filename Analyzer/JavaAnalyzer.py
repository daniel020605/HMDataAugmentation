import os
import javalang

def find_android_imports(tree):
    imports = {}
    for imp in tree.imports:
        class_name = imp.path.split('.')[-1]
        imports[class_name] = imp.path
    return imports

def find_android_method_calls(file_path):
    with open(file_path, 'r') as f:
        code = f.read()

    try:
        tree = javalang.parse.parse(code)
    except javalang.parser.JavaSyntaxError:
        return []

    imports = find_android_imports(tree)
    results = []
    for path, node in tree.filter(javalang.tree.MethodInvocation):
        class_name = resolve_qualified_name(node.qualifier, imports) if node.qualifier else ""
        method_name = node.member
        line = node.position.line if node.position else 0

        if is_android_api(class_name):
            results.append({
                "class": class_name,
                "method": method_name,
                "line": line,
                "file": file_path
            })

    return results

def resolve_qualified_name(qualifier, imports):
    return imports.get(qualifier, qualifier)

def is_android_api(class_name: str) -> bool:
    return class_name.startswith(('android.', 'androidx.'))

def traverse_android_project(root_path):
    all_results = []
    for subdir, _, files in os.walk(root_path):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(subdir, file)
                results = find_android_method_calls(file_path)
                all_results.extend(results)
    return all_results

if __name__ == '__main__':
    project_path = '/Users/daniel/Desktop/Android/FakeBiliBili'
    results = traverse_android_project(project_path)
    for r in results:
        relative_path = os.path.relpath(r['file'], project_path)
        print(f"Class: {r['class']}, Method: {r['method']}, Line: {r['line']}, File: {relative_path}")