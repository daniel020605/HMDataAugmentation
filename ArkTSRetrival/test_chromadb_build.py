from chromadb.utils import embedding_functions
import chromadb
import json
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter  # 使用 LangChain 的分块工具
from openai import OpenAI


file_path = 'data/extracted_harmonyos-references.json'
chroma_client = chromadb.PersistentClient(path="./t_chroma_db")

BAAI_ef = embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                                                api_base="https://api.siliconflow.cn/v1/",
                                                api_key="sk-cjvcxzatusoigdfrvbrdlkflncunldopmrfvkdhhbhynzlpw",
                                                model_name="BAAI/bge-m3",
                                             )

# ===== 新增分块配置 =====
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=256,       # 每个块的字符数
    chunk_overlap=50,     # 块间重叠字符数
    separators=["\n\n", "\n", "。", "；"]  # 中文优先分割符
)


def create():
    collection_1 = chroma_client.get_or_create_collection(name="t_HM_data_function_name", 
                                                embedding_function= BAAI_ef,)

    collection_2 = chroma_client.get_or_create_collection(name="t_HM_data_code", 
                                                embedding_function= BAAI_ef,)

    collection_3 = chroma_client.get_or_create_collection(name="t_HM_data_full_code",
                                                embedding_function= BAAI_ef,)
    
    return collection_1, collection_2, collection_3

# ===== 改造后的数据插入逻辑 =====
def process_entry(collection, entry):
    """带分块处理的数据插入函数"""
    raw_text = entry.get('pre', '')
    if not raw_text:
        return
    
    # 执行分块操作
    chunks = text_splitter.split_text(raw_text)
    
    # 为每个块生成唯一ID和元数据
    entry_id = str(entry.get('id'))  # 使用原始ID或块序号作为ID
    for i, chunk in enumerate(chunks):
        chunk_id = f"{entry_id}_chunk_{i}"  # 唯一ID格式：原始ID_块序号
        
        metadata = {
            "function_name": entry.get('function_name') or "default_function_name",
            "import_info": entry.get('import_module') or "default_import_info",
            "original_id": entry_id,        # 新增原始ID用于回溯原文
            "chunk_index": i,               # 记录块序号
            "total_chunks": len(chunks)      # 记录总块数
        }
        
        collection.add(
            documents=[chunk],
            metadatas=[metadata],
            ids=[chunk_id]
        )

# ===== 改造后的数据库构建流程 ===== 
def fullfill():
    collection_1, collection_2, collection_3 = create()
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    for entry in tqdm(data):
        # 只处理 Reference 类型数据到 collection_3
        if entry.get('type') == "Reference":
            process_entry(collection_3, entry)  # 使用分块插入
            
        # 其他集合的插入逻辑保持不变...
        # （保持你原有 collection_1/collection_2 的逻辑）

def search_with_chunks(collection, query, top_k=5):
    # 第一步：检索相关块
    results = collection.query(
        query_texts=[query],
        n_results=top_k*3  # 扩大召回量
    )
    
    # 第二步：结果聚合
    grouped = {}
    for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        original_id = meta['original_id']
        score = 1 - dist  # Convert distance to similarity score
        print("-------------")
        print(score)
        print("-------------")
        if original_id not in grouped:
            grouped[original_id] = {
                'score': score,
                'chunks': [doc],
                'metadata': meta
            }
        else:
            grouped[original_id]['score'] = max(grouped[original_id]['score'], score)
            grouped[original_id]['chunks'].append(doc)
    
    # 第三步：按聚合分数排序
    sorted_results = sorted(grouped.values(), key=lambda x: x['score'], reverse=True)
    return sorted_results[:top_k]

def chroma_search(query_code, topk=5):
    """
    使用chromadb进行向量检索
    返回: [(example, score), ...]
    """
    collection_1, collection_2, collection_3 = create()
    
    # Load the original examples to map back from chunk results
    with open(file_path, 'r') as f:
        examples = {str(item['id']): item for item in json.load(f)}
    
    # Get chunk results
    chunk_results = search_with_chunks(collection_3, query_code, top_k=topk)
    
    # Map chunks back to original examples and calculate scores
    output = []
    for result in chunk_results:
        original_id = result['metadata']['original_id']
        if original_id in examples:
            # Use the highest score among chunks for the example
            output.append((examples[original_id], result['score']))
    
    return output[:topk]
    
# ===== 测试代码 =====
collection_1, collection_2, collection_3 = create()
res = search_with_chunks(collection_3, "import { JSON } from '@kit.ArkTS'", top_k=5)
print(res)