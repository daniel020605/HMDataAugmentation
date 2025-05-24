import json
import re
from pathlib import Path
from typing import Dict, Optional


class ArkTSCodeSplitter:
    def __init__(self, entry_file: str, project_root: str):
        self.entry_file = Path(entry_file)
        self.project_root = Path(project_root)
        self.xl_context: Dict[str, str] = {}
        self.import_cache = set()

        # 智能分割配置
        self.split_priority = [
            self._split_at_function_body,
            self._split_at_class_method,
            self._split_at_control_flow,
            self._split_at_expression
        ]

    def analyze(self) -> dict:
        """主分析流程"""
        self._build_cross_file_context()
        main_content = self._read_file(self.entry_file)

        # 获取智能分割结果
        split_data = self._smart_split(main_content)

        return {
            "xl_context": self.xl_context,
            "above_context_without_fim_start": split_data["above"],
            "fim_task_sector_start": "",  # 无实际标记
            "fim_target": split_data["target"],
            "fim_task_sector_end": "",  # 无实际标记
            "follow_context_without_fim_end": split_data["follow"]
        }

    def _build_cross_file_context(self):
        """构建跨文件上下文"""
        stack = [self.entry_file]

        while stack:
            current_file = stack.pop()
            if str(current_file) in self.import_cache:
                continue

            self.import_cache.add(str(current_file))
            content = self._read_file(current_file)

            # 收集导出内容
            exports = self._extract_exports(content)
            self.xl_context[str(current_file.relative_to(self.project_root))] = content

            # 处理依赖
            for imp in self._extract_imports(content):
                resolved_path = self._resolve_import_path(current_file, imp["path"])
                if resolved_path and resolved_path.exists():
                    stack.append(resolved_path)

    def _smart_split(self, content: str) -> dict:
        """智能代码分割"""
        for splitter in self.split_priority:
            result = splitter(content)
            if result:
                return result
        return self._default_split(content)

    def _split_at_function_body(self, content: str) -> Optional[dict]:
        """在函数体中间分割"""
        fn_match = re.search(
            r'function\s+\w+\(.*?\)\s*{([^{}]*)}',
            content,
            re.DOTALL
        )
        if fn_match:
            body = fn_match.group(1)
            split_pos = fn_match.start(1) + len(body) // 2
            return {
                "above": content[:split_pos].strip(),
                "target": content[split_pos:fn_match.end(1)].strip(),
                "follow": content[fn_match.end(1):].strip()
            }

    def _split_at_class_method(self, content: str) -> Optional[dict]:
        """在类方法之间分割"""
        class_match = re.search(
            r'class\s+\w+\s*{([^}]*)}',
            content,
            re.DOTALL
        )
        if class_match:
            methods = re.findall(r'\b\w+\(.*?\)\s*{', class_match.group(1))
            if len(methods) > 1:
                mid = len(methods) // 2
                split_pos = content.find(methods[mid])
                return {
                    "above": content[:split_pos].strip(),
                    "target": methods[mid].strip(),
                    "follow": content[split_pos + len(methods[mid]):].strip()
                }

    def _split_at_control_flow(self, content: str) -> Optional[dict]:
        """在控制流语句处分割"""
        for keyword in ['if', 'for', 'while', 'switch']:
            match = re.search(
                fr'({keyword}\s*\(.*?\)\s*{{)(.*?)(}})',
                content,
                re.DOTALL
            )
            if match:
                body = match.group(2)
                split_pos = match.start(2) + len(body) // 2
                return {
                    "above": content[:split_pos].strip(),
                    "target": content[split_pos:match.end(2)].strip(),
                    "follow": content[match.end(2):].strip()
                }

    def _split_at_expression(self, content: str) -> Optional[dict]:
        """在表达式级别分割"""
        expressions = re.split(r';(?![^{]*})', content)
        if len(expressions) > 1:
            mid = len(expressions) // 2
            return {
                "above": ';'.join(expressions[:mid]).strip(),
                "target": expressions[mid].strip(),
                "follow": ';'.join(expressions[mid + 1:]).strip()
            }

    def _default_split(self, content: str) -> dict:
        """默认行级分割"""
        lines = [line for line in content.split('\n') if line.strip()]
        if not lines:
            return {"above": "", "target": "", "follow": ""}

        mid = len(lines) // 2
        return {
            "above": '\n'.join(lines[:mid]),
            "target": lines[mid],
            "follow": '\n'.join(lines[mid + 1:])
        }

    def _resolve_import_path(self, base_path: Path, import_path: str) -> Path:
        """解析导入路径"""
        if import_path.startswith('.'):
            return (base_path.parent / import_path).with_suffix('.ets')
        return self.project_root / 'node_modules' / import_path

    def _extract_imports(self, content: str) -> list:
        """提取导入语句"""
        imports = []
        pattern = r"import\s+(?:(\w+)|{([\w\s,]+)})\s+from\s+['\"](.+?)['\"];"
        for match in re.finditer(pattern, content):
            path = match.group(3)
            imports.append({"path": path})
        return imports

    def _extract_exports(self, content: str) -> str:
        """提取导出内容"""
        exports = []
        for match in re.finditer(r'export\s+(function|class|interface)\s+(\w+)', content):
            exports.append(f"{match.group(1)} {match.group(2)}")
        return '\n'.join(exports)

    def _read_file(self, path: Path) -> str:
        """读取文件内容"""
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {path}: {str(e)}")
            return ""


# 使用示例
if __name__ == "__main__":
    splitter = ArkTSCodeSplitter(
        entry_file="entry/src/test/List.test.ets",
        project_root="."
    )

    result = splitter.analyze()

    print(json.dumps(result, indent=2, ensure_ascii=False))