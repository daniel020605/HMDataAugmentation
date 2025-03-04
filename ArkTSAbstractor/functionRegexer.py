import re

# 正则表达式模式
patterns = {
    'function_decl': re.compile(
        r'function\s+(\w+)\s*\(([\s\S]*?)\)\s*(?::\s*([^{]+?))?\s*\{',
        re.DOTALL
    ),
    'arrow_func': re.compile(
        r'let\s+(\w+)\s*=\s*\(([\s\S]*?)\)\s*(?::\s*([^=>]+?))?\s*=>\s*([\s\S]*?)(;|\{)',
        re.DOTALL
    ),
    'overload_decl': re.compile(
        r'function\s+(\w+)\s*\(([\s\S]*?)\)\s*(?::\s*([^;]+?))?\s*;',
        re.DOTALL
    ),
}

param_pattern = re.compile(
    r'\s*(\.\.\.)?(\w+)(\??)\s*:\s*([^=,]+?)(?:\s*=\s*(.*))?\s*$'
)


def parse_parameters(param_str):
    params = []
    param_list = [p.strip() for p in param_str.split(',') if p.strip()]
    for param in param_list:
        match = param_pattern.match(param)
        if match:
            groups = match.groups()
            is_rest = groups[0] is not None
            name = groups[1]
            optional = groups[2] == '?' or groups[4] is not None
            param_type = groups[3].strip()
            default = groups[4].strip() if groups[4] else None
            params.append({
                'name': name,
                'type': param_type,
                'optional': optional,
                'rest': is_rest,
                'default': default
            })
        else:
            params.append({'error': f'Unparsed parameter: {param}'})
    return params


def analyze_code(code):
    functions = []

    # 匹配常规函数声明
    for match in patterns['function_decl'].finditer(code):
        name = match.group(1).strip()
        params_str = match.group(2).strip()
        return_type = match.group(3).strip() if match.group(3) else None
        params = parse_parameters(params_str)
        functions.append({
            'type': 'function',
            'name': name,
            'parameters': params,
            'return_type': return_type
        })

    # 匹配箭头函数
    for match in patterns['arrow_func'].finditer(code):
        var_name = match.group(1).strip()
        params_str = match.group(2).strip()
        return_type = match.group(3).strip() if match.group(3) else None
        body = match.group(4).strip()
        params = parse_parameters(params_str)
        functions.append({
            'type': 'arrow_function',
            'variable': var_name,
            'parameters': params,
            'return_type': return_type,
            'body': body
        })

    # 匹配重载声明
    overloads = {}
    for match in patterns['overload_decl'].finditer(code):
        name = match.group(1).strip()
        params_str = match.group(2).strip()
        return_type = match.group(3).strip() if match.group(3) else None
        params = parse_parameters(params_str)
        if name not in overloads:
            overloads[name] = []
        overloads[name].append({
            'parameters': params,
            'return_type': return_type
        })

    # 将重载声明加入结果
    for name, decls in overloads.items():
        functions.append({
            'type': 'overload',
            'name': name,
            'declarations': decls
        })

    return functions


# 测试代码
test_code = """
function add(x: string, y: string): string {
  let z: string = `${x} ${y}`;
  return z;
}

function hello(name?: string) {
  if (name == undefined) {
    console.log('Hello!');
  } else {
    console.log(`Hello, ${name}!`);
  }
}

function multiply(n: number, coeff: number = 2): number {
  return n * coeff;
}

function sum(...numbers: number[]): number {
  let res = 0;
  for (let n of numbers)
    res += n;
  return res;
}

let sum = (x: number, y: number): number => {
  return x + y;
}

let sum2 = (x: number, y: number) => x + y;

function foo(x: number): void;
function foo(x: string): void;
function foo(x: number | string): void {  /* 实现 */ }
"""

result = analyze_code(test_code)
for func in result:
    print(func)