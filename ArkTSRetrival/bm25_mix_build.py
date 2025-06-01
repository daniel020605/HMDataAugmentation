import re
from rank_bm25 import BM25Okapi
import chromadb
import jieba

# ===== 代码专用预处理 =====
class CodePreprocessor:
    @staticmethod
    def extract_imports(text):
        patterns = [
            r'^import\s+[\w\.]+',          
            r'^import\s+[{}\w\.]+\s+from\s+[@\w\.]+',    
        ]
        imports = []
        for line in text.split('\n'):
            for pattern in patterns:
                match = re.search(pattern, line.strip())
                if match:
                    imports.append(line.strip())
                    break
        return imports

    @staticmethod
    def clean_code(text):
        """保留代码结构的关键清洗：
        1. 移除字符串内容（保留引号占位）
        2. 保留注释标记但移除注释内容
        3. 标准化缩进
        """
        # 移除字符串内容
        text = re.sub(r'(["\'])(?:(?=(\\?))\2.)*?\1', r'\1...\1', text)
        # 移除注释内容但保留注释标记
        text = re.sub(r'#.*', '#', text)          # Python
        text = re.sub(r'//.*', '//', text)        # JS/Java
        text = re.sub(r'/\*.*?\*/', '/* */', text, flags=re.DOTALL)
        # 标准化缩进为单空格
        text = re.sub(r'\t', '    ', text)
        return text

# ===== 场景化混合检索器 =====
class CodeHybridRetriever(HybridRetriever):
    def _build_bm25_index(self):
        all_docs = self.collection.get()['documents']
        all_ids = self.collection.get()['ids']
        
        # 代码专用分词器
        tokenized_docs = []
        for doc in all_docs:
            # 关键代码元素提取
            cleaned = CodePreprocessor.clean_code(doc)
            # 按编程语言符号分词
            tokens = re.findall(r'\w+|\{|\}|\(|\)|\.|=>|:', cleaned)
            tokenized_docs.append(tokens)
        
        return BM25Okapi(tokenized_docs), {i:id for i,id in enumerate(all_ids)}
    
    def search(self, query, top_k=5, alpha=0.6):  # 默认提高 BM25 权重
        # 提取查询中的包引用
        query_imports = CodePreprocessor.extract_imports(query)
        
        # 如果查询包含包引用，优先提升其权重
        boosted_query = query
        if query_imports:
            boosted_query += " " + " ".join(query_imports) * 2  # 重复包引用词提升 BM25 权重
            
        return super().search(boosted_query, top_k, alpha)

# ===== 检索示例 =====
retriever = CodeHybridRetriever(collection_3)

# 案例：查询包含包引用的代码片段
query_code = '''
import pandas as pd
df = pd.read_csv("data.csv")
'''

results = retriever.search(query_code, alpha=0.7)  # 更侧重包引用匹配